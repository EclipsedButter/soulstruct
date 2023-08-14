"""Classes for MCG and MCP files, and other navmesh-related tools.

Currently only set up for DS1R.

Detailed information about the relationship between MSB navmeshes and collisions, MCP files, and MCG files:

    - A navmesh is a simple mesh comprised of triangular faces. Each face has a certain flag associated with it, which
    are enumerated in `NavmeshTyping` (e.g. "Solid", "Wall", "Cliff", "Ladder").

    - Enemy pathing is plotted out as a sequence of moves from face to face (to the center of each face, specifically).
    Some enemies are not permitted to have paths planned out over faces with certain flags (e.g. only some characters
    can climb ladders).

    - Navmeshes are generally (about 95% of the time) 1:1 with collisions and generally have matching model indices
    (e.g. "n0003B0" is generally congruent with collision "h0003B0"). Sometimes, one navmesh can cover multiple
    collisions, but I don't believe I've seen one collision cover multiple navmeshes in DS1.

    - Each navmesh in a map has a corresponding "room" in that map's MCP file. These rooms simply index the navmeshes
    in the order they are contained inside the MSB. These rooms are simple "AABBs" (axis-aligned bounding boxes) aligned
    to the world axes, so they aren't particularly veridical to the map geometry. (I would guess that they are generated
    in a way that contains all navmesh vertices in that model, plus some padding.) Each room is connected to a list of
    other rooms.

    - Each map also has an MCG file containing a graph that helps AI use the navmesh. The nodes in this graph are
    "gates" between MCP rooms, with "edges" connecting them that each pass through one room index from the MCP (or
    equivalently, one navmesh part in the MSB).

    - The MCP navmesh rooms control *backread*, based on the player's distance from that room's box (likely a simple
    raycast). The game also only seems to check the distance to rooms that are connected to the one the player is
    standing inside (or was last standing inside). This is why it is CRITICAL that your MCP files are accurate to your
    navmeshes, particularly for connections between maps (as the backread status of other maps' collisions REQUIRES this
    navmesh raycast to succeed, whereas collisions inside the same map can use display groups).

    - The "navmesh groups" of navmeshes that are in backread (because their corresponding rooms are close enough and
    connected) are used to upgrade two backread tables, one "normal" (possibly characters, objects, etc., or possibly
    unused) and one "hit" (collisions). In DS1, the distances for "normal" backread (enabled at 20m, disabled at 25m)
    are smaller than for "hit" backread (enabled after spending 0.2s closer than 80m, disabled after spending 1.3s
    further than 90m). You can play with these values in the debug menu (`GAME > WorldBackRead`).

    - By default (i.e. without any navmeshes and no navmesh-produced backread), the player's current collision has
    backread 4 (low + hi poly versions), all other collisions in the current map have backread 2 (low poly only), and
    all collisions in all other loaded maps have backread 0.

    - These backreads states are "upgraded" by navmesh backread groups. If a navmesh's MCP AABB is within the "hit"
    backread distance, it achieves a non-zero backread level (2) and is loaded (appears under "WorldBackRead" menu).
    However, only its low-poly version is loaded.

    - The distance to the room the player is current inside is always 0.0. If the player is standing inside multiple
    rooms, the game appears to prefer the room that matches the player's navmesh, or that is inside the map of the
    player's current collision? Unclear exactly how this preferential system works, but it does seem that the game only
    checks the distance of rooms that are linked to the last room the player was inside.

    - Any collisions whose navmesh groups are covered by the navmesh group of a triggered navmesh will be "upgraded".
    Collisions in the current map will go from backread 2 to backread 4. Collisions in connected maps will go from
    backread 0 to backread 2.

    - That is, navmesh groups and an intact navmesh-produced backread system are NECESSARY to get collisions in other
    connected maps to load. The connection's display groups alone can't get backread high enough to give the other map's
    collisions any actual physics!

    - The *draw groups* of collisions appear to be used for *children only*! Actual collision physics are determined
    solely by backread state, which is determined by navmesh rooms and navmesh groups.

Notes for functional navmesh system:

    - Every navmesh must have at least one "related" node. Related nodes are nodes that have an edge passing through
    that navmesh's AABB (as referenced by `edge.connected_aabb`) or nodes that explicitly reference that AABB through
    their `node.connected_aabb` attribute. The game uses this direct connection IF AND ONLY IF the navmesh has no nodes
    that are related through edges - that is, a "dead end" navmesh that has no edges within it.

    - Every navmesh must have at least one connected AABB in its `aabb.connected_aabbs` attribute, or it will never
    enter backread, even when standing on it (and may screw up other navmeshes nearby as well).

    - Gate node positions do not affect backread, but the connectivity BETWEEN them does seem to inform which navmeshes
    can enter backread from a distance. As long as the two requirements above are met (and `MapConnection` instances are
    set up properly), you will probably be able to navigate the world without issues, as navmeshes enter backread "just
    in time" when walking on them, but proper connected nodes are needed for the actual raycasting 80m/90m system to
    work. This will need to be done for enemy behavior anyway.

    - It should go without saying that breaking correspondence between the connected nodes and edges of nodes will
    cause major issues, so don't do this. You can tell if the navmesh system is broken completely because that map will
    not appear as an option at the bottom of the debug `WorldNvmMan` menu.

Miscellaneous extra notes (made long after the above):

    - MCG gates are definitely used to determine map backread. If you're near a gate that has a connection to a gate
    that is near a connect collision ("near" being somehow determined by physical navmeshes), that map will enter
    backread.
"""

from __future__ import annotations

__all__ = [
    "NavmeshGraph",
]

import logging
import typing as tp
from dataclasses import dataclass
from pathlib import Path

from soulstruct.darksouls1ptde.maps.msb import MSB as PTDE_MSB
from soulstruct.darksouls1r.maps.parts import MSBNavmesh
from soulstruct.utilities.maths import Vector3

from .mcp import MCP, NavmeshAABB
from .mcg import MCG, GateNode, GateEdge
from .utilities import ExistingConnectionError, MissingConnectionError, import_matplotlib_plt

_LOGGER = logging.getLogger(__name__)

NavmeshTyping = tp.Union[MSBNavmesh, str, int]


@dataclass(slots=True, init=False)
class NavmeshGraph:
    """Wrapper that handles `MCP` and `MCG` instances/files for the navmesh parts in a given `MSB`.

    Designed to be a friendlier and less painful interface for navmesh graph editing than those classes themselves, as
    both files need to be kept in tight correspondence to the MSB navmesh parts and face indices in their models.

    Methods with arguments that require navmeshes support `MSBNavmesh` instances or names/indices thereof in the MSB.

    Never edits or writes the MSB, only uses it to retrieve `MSBNavmesh` part instances.

    Args:
        map_path (str or Path): Folder containing MCP and MCG files (e.g. '{game_root}/map/m10_01_00_00').
        msb (MSB or None): MSB instance or file path. If None (default), searched for in adjacent `MapStudio` directory.
        map_stem (str): map name stem, e.g. 'm10_01_00_00'. Auto-detected from `map_path` directory name by default.
    """

    map_path: Path  # path to game `map/mAA_BB_CC_DD` directory (NOT `MapStudio`)
    map_stem: str  # detected from `map_path` by default
    map_id: tuple[int, int, int, int]  # map ID tuple for AABBs and edges (e.g. `(10, 1, 0, 0)`)

    msb_path: Path
    mcp: MCP
    mcg: MCG
    _msb: PTDE_MSB  # MSB to pull navmeshes from; read from `MapStudio` adjacent to `map_path` by default

    def __init__(self, map_path: Path | str, msb: PTDE_MSB = None, map_stem: str = None):
        self.map_path = Path(map_path)
        if not self.map_path.is_dir():
            raise ValueError(f"Map directory does not exist: {self.map_path}")
        self.map_stem = self.map_path.name if map_stem is None else map_stem
        aa, bb, cc, dd = [int(x) for x in self.map_stem[1:].split("_")]
        self.map_id = (aa, bb, cc, dd)

        if msb is None:
            self.msb_path = (self.map_path / f"../MapStudio/{self.map_stem}.msb").resolve()
            try:
                self._msb = PTDE_MSB.from_path(self.msb_path)
            except FileNotFoundError:
                raise FileNotFoundError(f"Could not find MSB file: {self.msb_path}")
        elif isinstance(msb, PTDE_MSB):
            if not msb.path:
                raise ValueError("`MSB` given to `NavInfo` must have `.path` set.")
            self._msb = msb
            self.msb_path = msb.path
        else:
            raise TypeError(
                f"`MSB` given to `NavInfo` has invalid type: `{msb.__class__.__name__}`. Note that only PTDE or DSR "
                f"`MSB` subclasses are supported."
            )

        mcp_path = self.map_path / f"{self.map_stem}.mcp"
        mcg_path = self.map_path / f"{self.map_stem}.mcg"
        try:
            self.mcp = MCP.from_path(mcp_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find MCP file: {str(mcp_path)}")
        try:
            self.mcg = MCG.from_path(mcg_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find MCG file: {str(mcg_path)}")

        # Set navmesh part references in MCG edges (all) and nodes (if they have a dead-end navmesh).
        self.mcg.set_navmesh_references(self._msb.navmeshes)

    @property
    def msb(self):
        """You can't change the attached MSB instance."""
        return self._msb

    @property
    def navmeshes(self):
        """Shortcut for getting list of Navmesh instances from MSB parts."""
        return self._msb.navmeshes

    @property
    def aabbs(self):
        return self.mcp.aabbs

    @property
    def nodes(self):
        return self.mcg.nodes

    @property
    def edges(self):
        return self.mcg.edges

    def _get_navmesh(self, navmesh: NavmeshTyping) -> MSBNavmesh:
        """Get `MSBNavmesh` instance from `NavmeshTyping` (either `MSBNavmesh` instance or name/index in MSB)."""
        if isinstance(navmesh, MSBNavmesh):
            if navmesh not in self.navmeshes:
                raise ValueError(f"Navmesh '{navmesh.name}' is not a part in the attached MSB.")
            return navmesh
        elif isinstance(navmesh, str):
            return self._msb.navmeshes.find_entry_name(navmesh)
        elif isinstance(navmesh, int):
            return self._msb.navmeshes[navmesh]
        raise TypeError(f"Invalid navmesh type: {navmesh.__class__.__name__}. Must be `MSBNavmesh`, str, or int.")

    def check_aabb_count(self):
        """Raises a `NavmeshSyncError` if the number of MSB Navmeshes does not match the number of MCP AABBs.

        This will no doubt occur briefly as new `MSB` and `NavInfo` instances are constructed, but most `NavInfo`
        methods should not be called at that time.
        """
        # TODO: Convert to decorator once PyCharm fixes decorator `self` issue.
        if (navmesh_count := len(self.navmeshes)) != (aabb_count := len(self.mcp.aabbs)):
            raise ValueError(
                f"Number of navmeshes in MSB ({navmesh_count}) does not match the number of AABBs in "
                f"MCP ({aabb_count}). This should be fixed ASAP, or navmesh functionality will be broken."
            )

    def get_navmesh_gate_nodes(self, navmesh: NavmeshTyping) -> list[GateNode]:
        """Return all MCG nodes with at least one edge in the given navmesh or who explicitly have this navmesh as
        their dead-end navmesh."""
        navmesh = self._get_navmesh(navmesh)
        return [
            node for node in self.nodes
            if any(edge.navmesh is navmesh for edge in node.connected_edges)
            or node.dead_end_navmesh is navmesh
        ]

    def get_navmesh_aabb(self, navmesh: NavmeshTyping) -> NavmeshAABB:
        """Get `NavmeshAABB` with the same index as `navmesh` index in MSB.

        `navmesh` can be an `MSBNavmesh` entry or the name of one. Obviously, if you already have its index in the MSB,
        you can look up the AABB directly already.
        """
        self.check_aabb_count()
        navmesh = self._get_navmesh(navmesh)
        navmesh_index = self.navmeshes.index(navmesh)
        return self.mcp.aabbs[navmesh_index]

    def get_navmesh_aabb_connected_navmeshes(self, navmesh: NavmeshTyping) -> list[MSBNavmesh]:
        """Get all navmesh parts connected to `navmesh` via AABB connectivity in MCP file."""
        aabb = self.get_navmesh_aabb(navmesh)
        return [self.navmeshes[i] for i in aabb.connected_navmesh_part_indices]

    def new_node(
        self,
        translate: Vector3,
        unknown_offset=0,
        dead_end_navmesh: MSBNavmesh = None,
    ) -> GateNode:
        """Create and return a new `GateNode` with the given `translate` and optional `dead_end_navmesh`.

        Does not create any connections to other nodes; other methods in this wrapper class should be used for that.
        """
        node = GateNode(translate=translate, unknown_offset=unknown_offset, dead_end_navmesh=dead_end_navmesh)
        self.mcg.nodes.append(node)
        return node

    def remove_node(self, node: GateNode | int):
        """Delete given node and any edges to it.

        Obviously, this will change all node indices that come after it, so be careful.
        """
        if isinstance(node, int):
            node = self.mcg.nodes[node]
        elif node not in self.mcg.nodes:
            raise ValueError("Given `node` does not appear in this `NavmeshGraph`.")
        node_edges = [e for e in self.mcg.edges if node is e.start_node or node is e.end_node]
        for edge in node_edges:
            self.mcg.delete_edge(edge)  # will also remove all references to `node` from other nodes
        self.mcg.nodes.remove(node)

    def connect_nodes(
        self,
        start_node: GateNode | int,
        end_node: GateNode | int,
        edge_navmesh: NavmeshTyping,
        start_node_triangle_indices: list[int],
        end_node_triangle_indices: list[int],
        cost: float = None,
        ignore_connected=False,
    ):
        """Connect two nodes with a new edge with the given fields."""
        navmesh = self._get_navmesh(edge_navmesh)
        self.mcg.connect_nodes(
            start_node=start_node,
            end_node=end_node,
            edge_navmesh=navmesh,
            start_node_navmesh_triangle_indices=start_node_triangle_indices,
            end_node_navmesh_triangle_indices=end_node_triangle_indices,
            cost=cost,
            ignore_connected=ignore_connected,
        )

    def connect_navmesh_aabbs(
        self,
        first_navmesh: NavmeshTyping,
        second_navmesh: NavmeshTyping,
        ignore_connected=False,
    ):
        """Connect the two AABBs of the given navmeshes.

        Does NOT modify nodes or edges.
        """
        self.check_aabb_count()
        first_navmesh = self._get_navmesh(first_navmesh)
        second_navmesh = self._get_navmesh(second_navmesh)
        first_navmesh_index = self.navmeshes.index(first_navmesh)
        second_navmesh_index = self.navmeshes.index(second_navmesh)
        first_aabb = self.mcp.aabbs[first_navmesh_index]
        second_aabb = self.mcp.aabbs[second_navmesh_index]
        if (
            first_navmesh_index in second_aabb.connected_navmesh_part_indices
            and second_navmesh_index in first_aabb.connected_navmesh_part_indices
        ):
            if ignore_connected:
                return  # do nothing
            raise ExistingConnectionError("Given AABBs are already connected.")
        if second_navmesh_index not in first_aabb.connected_navmesh_part_indices:
            first_aabb.connected_navmesh_part_indices.append(second_navmesh_index)
        if first_navmesh_index not in second_aabb.connected_navmesh_part_indices:
            second_aabb.connected_navmesh_part_indices.append(first_navmesh_index)

    def disconnect_navmesh_aabbs(
        self,
        first_navmesh: NavmeshTyping,
        second_navmesh: NavmeshTyping,
        ignore_unconnected=False,
    ):
        """Disconnect the two given MCP AABBs, which can also be given as MSB navmeshes or names thereof.

        Does NOT modify nodes or edges.
        """
        self.check_aabb_count()
        first_navmesh = self._get_navmesh(first_navmesh)
        second_navmesh = self._get_navmesh(second_navmesh)
        first_navmesh_index = self.navmeshes.index(first_navmesh)
        second_navmesh_index = self.navmeshes.index(second_navmesh)
        first_aabb = self.mcp.aabbs[first_navmesh_index]
        second_aabb = self.mcp.aabbs[second_navmesh_index]
        if (
            first_navmesh_index not in second_aabb.connected_navmesh_part_indices
            and second_navmesh_index not in first_aabb.connected_navmesh_part_indices
        ):
            if ignore_unconnected:
                return  # do nothing
            raise MissingConnectionError("Given navmesh AABBs are not connected.")

        if second_navmesh_index in first_aabb.connected_navmesh_part_indices:
            first_aabb.connected_navmesh_part_indices.remove(second_navmesh_index)
        if first_navmesh_index in second_aabb.connected_navmesh_part_indices:
            second_aabb.connected_navmesh_part_indices.remove(first_navmesh_index)

    def add_aabbs_nodes_edges(
        self,
        aabbs: tp.Iterable[NavmeshAABB],
        nodes: tp.Iterable[GateNode],
        edges: tp.Iterable[GateEdge],
    ):
        """Add new AABBs, nodes, and edges to this `NavInfo` instance simultaneously.

        These new entry instances should generally only contain references to one another, and (for AABBs in particular)
        be added synchronously with MSB navmesh parts to ensure a 1:1 mapping.

        Note that every navmesh/AABB index must have at least one related node, with an edge passing through it or a
        direction reference through `node.connected_aabb`. Navmeshes with no related nodes will not function properly,
        even for collision backread, where the nodes' actual positions don't matter.

        TODO: Currently just being used to copy instances from a vanilla `NavmeshGraph` over to a new, empty instance.
            Would be preferable to simply reassign the MSB and update all `MSBNavmesh` references in this case!
            (Actually, how is this even good as-is if the copied nodes/edges have stale, vanilla MSB references?)
        """
        self.aabbs.extend(aabbs)
        self.nodes.extend(nodes)
        self.edges.extend(edges)

    def move_in_world(
        self,
        start_translate: Vector3 | list | tuple = None,
        end_translate: Vector3 | list | tuple = None,
        start_rotate: Vector3 | list | tuple | int | float = None,
        end_rotate: Vector3 | list | tuple | int | float = None,
        enclose_original=True,
        selected_aabbs: tp.Iterable[int | NavmeshAABB] = None,
        selected_nodes: tp.Iterable[int | GateNode] = None,
    ):
        """Rotate and then translate all AABBs in MCP (enclosing original AABBs by default) and all nodes in MCG in
        world coordinates, so that an entity with a translate of `start_translate` and rotate of `start_rotate` ends up
        with a translate of `end_translate` and a rotate of `end_rotate`.
        """
        self.mcp.move_in_world(
            start_translate,
            end_translate,
            start_rotate,
            end_rotate,
            enclose_original=enclose_original,
            selected_aabbs=selected_aabbs,
        )
        self.mcg.move_in_world(start_translate, end_translate, start_rotate, end_rotate, selected_nodes=selected_nodes)
        
    # TODO: To/from JSON methods for better version control. Just keep it simple at first: straight dataclass way.
    #  JSON can contain MSB navmesh part names and warn if they don't match the MSB passed to `from_json` (but the count
    #  is still correct).

    def to_string(self):
        """Print out a list of MCG nodes, their connections, and the AABBs those connective edges go through."""
        output = ""
        try:
            self.check_aabb_count()
            navmeshes_valid = True
        except ValueError as ex:
            navmeshes_valid = False
            output += f"WARNING: {ex}.\n"

        # TODO: Overhaul with navmesh part names leading the charge.
        for i, navmesh in enumerate(self.navmeshes):
            output += f"Navmesh {i} ({navmesh.name if navmeshes_valid else '???'})"
            if navmeshes_valid:
                aabb = self.get_navmesh_aabb(navmesh)
                output += f"  AABB start: {aabb.aabb_start}\n"
                output += f"  AABB end:   {aabb.aabb_end}\n"
                for connected_index in aabb.connected_navmesh_part_indices:
                    output += f"    --> Navmesh {self.navmeshes[connected_index]}\n"                    
            else:
                output += f"  AABB correspondence broken!\n"

        used_navmeshes = set()
        for i, node in enumerate(self.mcg.nodes):
            output += f"Node {i} [{node.translate}]:\n"
            for j, (connected_node, connected_edge) in enumerate(zip(node.connected_nodes, node.connected_edges)):
                connected_node_index = self.nodes.index(connected_node)
                used_navmeshes.add(connected_edge.navmesh)
                output += (f"Edge in {connected_edge.navmesh} ({connected_edge.start_node_triangle_indices} "
                           f"-> {connected_edge.end_node_triangle_indices}, cost = {connected_edge.cost})")
                output += f"    --> Node {connected_node_index}\n"
        for navmesh in self.navmeshes:
            if navmesh not in used_navmeshes:
                output += f"NO EDGES IN NAVMESH: {navmesh.name}\n"
        return output

    def draw(
        self,
        aabb_color="cyan",
        label_aabbs=True,
        label_nodes=True,
        axes=None,
        auto_show=True,
        focus_xzy=None,
        focus_size=50,
    ):
        plt = import_matplotlib_plt(raise_if_missing=True)

        if axes is None:
            fig = plt.figure(figsize=(8, 8))
            axes = fig.add_subplot(111, projection="3d")

        aabb_labels = [n.name for n in self.navmeshes] if label_aabbs else None
        node_labels = [
            f"{i} ({node.dead_end_navmesh.name})" if node.dead_end_navmesh else f"{i}"
            for i, node in enumerate(self.nodes)
        ] if label_nodes else None

        self.mcp.draw(aabb_color=aabb_color, aabb_labels=aabb_labels, axes=axes, auto_show=False)
        self.mcg.draw(node_labels=node_labels, axes=axes, auto_show=False)

        if focus_xzy is not None:
            x, z, y = focus_xzy
            axes.set(
                xlim=(x - focus_size, x + focus_size),
                ylim=(y - focus_size, y + focus_size),
                zlim=(z - focus_size, z + focus_size),
            )

        if auto_show:
            plt.show()
        return axes

    def write(self, map_path: Path | str = None):
        if map_path is None:
            mcp_path = mcg_path = None  # use original paths
        else:
            mcp_path = Path(map_path / f"{self.map_stem}.mcp")
            mcg_path = Path(map_path / f"{self.map_stem}.mcg")
        self.mcp.write(mcp_path)
        self.mcg.set_navmesh_indices(self.navmeshes)
        self.mcg.write(mcg_path)
        # Restore references after writing for further editing.
        self.mcg.set_navmesh_references(self.navmeshes)

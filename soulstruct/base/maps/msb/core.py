from __future__ import annotations

__all__ = ["MSB", "MSBSubtypeInfo"]

import abc
import logging
import re
import struct
import typing as tp
from dataclasses import dataclass, fields
from pathlib import Path

from soulstruct.base.game_file import GameFile
from soulstruct.base.game_types.map_types import MapEntity
from soulstruct.utilities.binary import *

from .msb_entry import MSBEntry
from .msb_entry_list import MSBEntryList
from .events import BaseMSBEvent
from .models import BaseMSBModel
from .parts import BaseMSBPart
from .regions import BaseMSBRegion
from .utils import MSBSubtypeInfo

try:
    Self = tp.Self
except AttributeError:
    Self = "MSB"

if tp.TYPE_CHECKING:
    from .enums import BaseMSBSubtype

_LOGGER = logging.getLogger(__name__)


MAP_NAME_RE = re.compile(r"m(\d\d)_(\d\d)_.*")
PY_NAME_RE = re.compile(r"^[A-z_][\w_]*$")  # valid Python variable name


# NOTE: Completely absent in DS1 and earlier.
MSB_HEADER_BYTES = struct.pack("4sII??BB", b"MSB ", 1, 16, False, False, 1, 255)
MSB_ENTRY_SUPERTYPES = {
    "MODEL_PARAM_ST": BaseMSBModel,
    "EVENT_PARAM_ST": BaseMSBEvent,
    "POINT_PARAM_ST": BaseMSBRegion,
    "PARTS_PARAM_ST": BaseMSBPart,
}
# Keys are lower-cased and 's' is removed from the end before they are checked in here.
MSB_ENTRY_SUPERTYPE_ALIASES = {
    "model": "MODEL_PARAM_ST",
    "event": "EVENT_PARAM_ST",
    "region": "POINT_PARAM_ST",
    "part": "PARTS_PARAM_ST",
}


@dataclass(slots=True)
class MSB(GameFile, abc.ABC):
    """Handles MSB ('MapStudio') data. Subclassed by each game.

    TODO: Update docstring.

    The MSB contains four types of data entries:

        Models: these are models that are available for map 'Part' entities such as map pieces, objects, characters,
            players, collisions, and navmeshes. Every Part included in the map will reference one of these models, and
            only models in this list will be loaded with the map.

        Events: these are 'things that happen' in the map, and are generally linked to Regions and/or Parts that have
            actual map coordinate data. There are numerous subtypes with additional data fields. Each event has an
            entity ID that may be referenced in the game events. There are no internal references to events inside the
            MSB, so they are never accessed by index and can be stored in any order.

        Regions: these are invisible points, shapes, and volumes that appear in the map. They are used to anchor events
            (e.g. spawn points, music, patrol points) and to perform location-based trigger checks in the game events
            (where they are referenced using their entity ID). Many MSB Events reference Regions by index, so their
            order needs to be carefully managed internally.

        Parts: these are actual map entities, including objects and characters. Each of them is linked to a model
            index, has a physical transform (translate, rotate, scale), and an optional entity ID. Characters and
            objects additionally have a collision index (their 'home' collision) and draw/display groups that determine
            when they are actually visible in the game. Some MSB Events reference Parts by index, so their order needs
            to be carefully managed internally.
    """
    EXT: tp.ClassVar[str] = ".msb"

    # TODO: Lots of info needed here.
    #  - Each superlist needs to know the offset to check for subtype int.
    #  - Need to map subtype int to subtype class.
    #   - Don't need a subtype enum anymore, really? Just dictionaries that map int <> class for reading/writing?

    # TODO: Other stuff:
    #  - Dictionary that contains common field info ('entity_id', etc.) that can be indexed.

    SUPERTYPE_LIST_HEADER: tp.ClassVar[tp.Type[NewBinaryStruct]]
    # Maps MSB entry supertype names (e.g. 'POINT_PARAM_ST') to dicts that map subtype ints to subtype info.
    MSB_ENTRY_SUBTYPES: tp.ClassVar[dict[str, dict[int, MSBSubtypeInfo]]]
    # Maps MSB entry superlist names (parts, etc.) to the relative offsets of their subtype enums.
    MSB_ENTRY_SUBTYPE_OFFSETS: tp.ClassVar[dict[str, int]]
    # Maps entry subtype names ("characters", "sounds", etc.) to their corresponding `BaseGameType`, if applicable.
    ENTITY_GAME_TYPES: tp.ClassVar[dict[str, MapEntity]]

    # Version info.
    HAS_HEADER: tp.ClassVar[bool]
    LONG_VARINTS: tp.ClassVar[bool]
    NAME_ENCODING: tp.ClassVar[str]

    # Subclasses define lists of entry subtypes here (`characters`, `sound_events`, `object_models`, etc.).

    @classmethod
    def from_reader(cls, reader: BinaryReader) -> Self:
        """Unpack an MSB from the given reader."""

        if cls.HAS_HEADER:
            header = reader.read(len(MSB_HEADER_BYTES))
            if header != MSB_HEADER_BYTES:
                raise AssertionError("Header of this MSB class did not match asserted header.")

        offset_fmt = "q" if cls.LONG_VARINTS else "i"

        # This will contain both supertype lists (e.g. "PARTS_PARAM_ST") and `MSBEntryList`s (e.g. "objects").
        entry_lists = {}  # type: dict[str, MSBEntryList[MSBEntry] | list[MSBEntry]]

        for supertype_name in MSB_ENTRY_SUPERTYPES:
            supertype_list_header = cls.SUPERTYPE_LIST_HEADER.from_bytes(reader)
            entry_offset_count = supertype_list_header.pop("entry_offset_count")  # includes final offset to next list
            name_offset = supertype_list_header.pop("name_offset")
            entry_offsets = list(reader.unpack(f"{entry_offset_count}{offset_fmt}"))
            found_name = reader.unpack_string(offset=name_offset, encoding=cls.NAME_ENCODING)
            if found_name != supertype_name:
                raise ValueError(f"MSB internal list name '{found_name}' != expected name '{supertype_name}'.")
            for entry_offset in entry_offsets[:-1]:  # exclude last offset
                reader.seek(entry_offset)
                cls._unpack_entry(reader, found_name, entry_lists)
            reader.seek(entry_offsets[-1])

        # Resolve entry indices to actual object references.
        for event in entry_lists["EVENT_PARAM_ST"]:
            event: BaseMSBEvent
            event.indices_to_objects(entry_lists)

        for part in entry_lists["PARTS_PARAM_ST"]:
            part: BaseMSBPart
            part.indices_to_objects(entry_lists)

        for supertype_name in MSB_ENTRY_SUPERTYPES:
            entry_lists.pop(supertype_name)  # only pass subtype lists to constructor

        # noinspection PyArgumentList
        return cls(**entry_lists)

    @classmethod
    def _unpack_entry(cls, reader: BinaryReader, supertype_name: str, entry_lists: dict[str, list[MSBEntry]]):
        subtype_int = reader.unpack_value("i", offset=reader.position + cls.MSB_ENTRY_SUBTYPE_OFFSETS[supertype_name])
        subtype_info = cls.MSB_ENTRY_SUBTYPES[supertype_name][subtype_int]
        subtype_class = subtype_info.entry_class
        entry = subtype_class.from_msb_reader(reader)
        # Put entry into appropriate supertype and subtype lists (creating if necessary).
        entry_lists.setdefault(supertype_name, []).append(entry)
        if subtype_info.subtype_list_name not in entry_lists:
            entry_lists[subtype_info.subtype_list_name] = MSBEntryList(
                supertype_name=supertype_name, subtype_info=subtype_info
            )
        entry_lists[subtype_info.subtype_list_name].append(entry)

    @staticmethod
    def resolve_supertype_name(supertype_name: str):
        if (alias := supertype_name.lower().rstrip()) in MSB_ENTRY_SUPERTYPE_ALIASES:
            return MSB_ENTRY_SUPERTYPE_ALIASES[alias]
        if supertype_name not in MSB_ENTRY_SUPERTYPES:
            raise ValueError(f"Invalid MSB supertype name: {supertype_name}")
        return supertype_name

    def get_supertype_list(self, supertype_name: str) -> list[MSBEntry]:
        """Construct a list of all MSB entries with the given supertype (e.g. "PARTS_PARAM_ST")."""
        supertype_name = self.resolve_supertype_name(supertype_name)
        supertype_list = []
        for subtype_list in self:
            if subtype_list.supertype_name == supertype_name:
                supertype_list.extend(subtype_list)
        return supertype_list

    def get_models(self) -> list[BaseMSBModel]:
        # noinspection PyTypeChecker
        return self.get_supertype_list("MODEL_PARAM_ST")

    def get_events(self) -> list[BaseMSBEvent]:
        # noinspection PyTypeChecker
        return self.get_supertype_list("EVENT_PARAM_ST")

    def get_regions(self) -> list[BaseMSBRegion]:
        # noinspection PyTypeChecker
        return self.get_supertype_list("POINT_PARAM_ST")

    def get_parts(self) -> list[BaseMSBPart]:
        # noinspection PyTypeChecker
        return self.get_supertype_list("PARTS_PARAM_ST")

    def get_list_of_entry(self, entry: MSBEntry) -> MSBEntryList:
        """Find subtype list that contains `entry` (e.g. for an event's attached region/part)."""
        for entry_list in self:
            if entry in entry_list:
                return entry_list
        raise ValueError(f"Entry '{entry.name}' does not appear anywhere in this MSB.")

    def to_writer(self) -> BinaryWriter:
        entry_lists = {name: getattr(self, name) for name in self.get_subtype_list_names()}
        for supertype_name in MSB_ENTRY_SUPERTYPES:
            entry_lists[supertype_name] = self.get_supertype_list(supertype_name)

        # Check for duplicate names within supertypes (except events, where duplicates are permitted and common).
        for supertype_name in ("MODEL_PARAM_ST", "POINT_PARAM_ST", "PARTS_PARAM_ST"):
            names = set()
            for entry in entry_lists[supertype_name]:
                if entry.name in names:
                    _LOGGER.warning(f"Duplicate '{supertype_name}' name in MSB: {entry.name}")
                else:
                    names.add(entry.name)

        # Get model instance counts.
        model_instance_counts = {}
        for part in entry_lists["PARTS_PARAM_ST"]:
            part: BaseMSBPart
            if part.model.name in model_instance_counts:
                model_instance_counts[part.model.name] += 1
            else:
                model_instance_counts[part.model.name] = 1

        # TODO: use writer.varint_size to communicate encoding?
        writer = BinaryWriter(byte_order=ByteOrder.LittleEndian, varint_size=8 if self.LONG_VARINTS else 4)
        if self.HAS_HEADER:
            writer.append(MSB_HEADER_BYTES)

        for supertype_name in MSB_ENTRY_SUPERTYPES:
            supertype_list = entry_lists[supertype_name]
            self.SUPERTYPE_LIST_HEADER.object_to_writer(
                self,
                writer,
                name_offset=RESERVED,
                entry_offset_count=len(supertype_list) + 1,  # includes final offset to next supertype list
            )
            for entry in supertype_list:
                writer.reserve("entry_offset", "v", obj=entry)
            writer.reserve("next_list_offset", "v", obj=supertype_list)

            writer.fill_with_position("name_offset", obj=self)
            packed_name = supertype_name.encode("ASCII")
            packed_name += b"\0" * (16 - len(packed_name))  # pad to 16 characters (NOTE: 32 in older Soulstruct)
            writer.append(packed_name)

            for supertype_index, entry in enumerate(supertype_list):
                entry: MSBEntry
                writer.fill_with_position("entry_offset", obj=entry)
                subtype_name = self.MSB_ENTRY_SUBTYPES[supertype_name][entry.SUBTYPE_ENUM.value].subtype_list_name
                subtype_index = entry_lists[subtype_name].index(entry)
                if supertype_name == "MODEL_PARAM_ST":
                    entry: BaseMSBModel
                    instance_count = model_instance_counts.get(entry.name, 0)
                    if instance_count == 0:
                        _LOGGER.warning(f"Model '{entry.name}' is not used by any parts in this MSB.")
                    entry.to_msb_writer(writer, supertype_index, subtype_index, entry_lists, instance_count)
                else:
                    try:
                        entry.to_msb_writer(writer, supertype_index, subtype_index, entry_lists)
                    except Exception as ex:
                        _LOGGER.error(
                            f"Exception occurred while trying to write entry '{entry.name}': {ex}.\n"
                            f"  Entry: {entry}"
                        )
                        raise

            if supertype_name == list(MSB_ENTRY_SUPERTYPES.values())[-1]:
                writer.fill("next_list_offset", 0, obj=supertype_list)  # zero offset
            else:
                writer.fill_with_position("next_list_offset", obj=supertype_list)

        return writer

    def find_entry_by_name(
        self, name: str, supertypes: tp.Iterable[str] = (), subtypes: tp.Iterable[str] = ()
    ) -> MSBEntry:
        """Get `MSBEntry` with name `name` that is one of the given `entry_subtypes` or any type by default.

        Raises a `KeyError` if the name cannot be found, and a `ValueError` if multiple entries are found.
        """
        if subtypes:  # lower case
            entry_lists = [getattr(self, f.lower()) for f in subtypes]  # type: list[MSBEntryList]
        else:
            entry_lists = self.get_all_subtype_lists()

        if supertypes:
            supertype_names = [self.resolve_supertype_name(name) for name in supertypes]
            entry_lists = [entry_list for entry_list in entry_lists if entry_list.supertype_name in supertype_names]

        results = []
        for subtype_list in entry_lists:
            try:
                # This will raise a `ValueError` if the name appears more than once in a single entry type list.
                results.append(subtype_list.find_entry_name(name))
            except KeyError:
                pass  # name does not appear in this list
        if not results:
            if supertypes and subtypes:
                type_msg = f"supertype in {supertypes} and subtype in {subtypes}"
            elif supertypes:
                type_msg = f"supertype in {supertypes}"
            elif subtypes:
                type_msg = f"subtype in {subtypes}"
            else:
                type_msg = "any type"
            raise KeyError(f"Could not find an entry named '{name}' with {type_msg} in MSB.")
        if len(results) > 1:
            raise ValueError(f"Found entries of multiple types with name '{name}': {list(results)}")
        return results[0]

    def to_dict(self, ignore_defaults=True) -> dict:
        """Return a dictionary form of the MSB.

        Fully serializes `MSBEntry` contents by converting inter-entry references to dictionaries.

        If `ignore_defaults=True` (default), entry fields that have the default values for that entry subclass will not
        be included in the entry's dictionary.

        NOTE: No MSB header information needs to be recorded. Just the version info.
        """
        entry_lists = self.get_all_subtype_lists()
        msb_dict = {"version": self.get_version_dict()}  # type: dict[str, dict[str, tp.Any]]
        for subtype_list in entry_lists:
            for supertype_name in MSB_ENTRY_SUPERTYPES:
                if subtype_list.supertype_name == supertype_name:
                    msb_dict.setdefault(supertype_name, {}).update(subtype_list.to_json_dict(self, ignore_defaults))
        return msb_dict

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Load MSB from dictionary of version info and entries (sorted by supertype and nested subtype keys)."""

        if "version" not in data:
            raise ValueError("MSB dictionary is missing 'version' key.")
        if data["version"] != cls.get_version_dict():
            raise TypeError(f"Invalid MSB 'version' info in dict for this MSB class: {data['version']}")

        subtype_list_names = cls.get_subtype_list_names()
        subtype_lists = {}
        for supertype_name in MSB_ENTRY_SUPERTYPES:
            if supertype_name not in data:
                _LOGGER.warning(f"No '{supertype_name}' key found in MSB dictionary, which is unusual.")
                continue
            subtype_dict = data[supertype_name]
            for subtype_name, subtype_list in subtype_dict.items():
                subtype_name = cls.resolve_subtype_name(subtype_name)
                if subtype_name not in subtype_list_names:
                    raise TypeError(f"Invalid MSB subtype name '{subtype_name}' (supertype '{supertype_name}').")
                subtype_info = [
                    info for _, info in cls.MSB_ENTRY_SUBTYPES[supertype_name].items()
                    if info.subtype_list_name == subtype_name
                ][0]
                # TODO: Have to defer entry reference dicts, construct the MSB below, then apply them all...
                entries = [subtype_info.entry_class.from_json_dict(entry_dict) for entry_dict in subtype_list]
                subtype_lists[subtype_name] = MSBEntryList(
                    *entries, supertype_name=supertype_name, subtype_info=subtype_info
                )

        # noinspection PyArgumentList
        return cls(**subtype_lists)

    @classmethod
    def get_version_dict(cls) -> dict[str, bool | str]:
        return {
            "has_header": cls.HAS_HEADER,
            "long_varints": cls.LONG_VARINTS,
            "name_encoding": cls.NAME_ENCODING,
        }

    @classmethod
    def get_subtype_list_names(cls) -> list[str]:
        return [field.name for field in fields(cls) if field.name not in {"path", "dcx_type"}]

    def get_all_subtype_lists(self) -> list[MSBEntryList]:
        return [getattr(self, list_name) for list_name in self.get_subtype_list_names()]

    @classmethod
    def resolve_subtype_name(cls, subtype_name: str):
        for subtype_info_list in cls.MSB_ENTRY_SUBTYPES.values():
            for info in subtype_info_list.values():
                if subtype_name in {info.subtype_list_name, info.subtype_enum.name, info.entry_class.__name__}:
                    return info.subtype_list_name
        raise KeyError(f"Invalid MSB subtype name: {subtype_name}")

    def resolve_entries_list(
        self,
        entries: tp.Sequence[str | MSBEntry],
        supertypes: tp.Iterable[str] = (),
        subtypes: tp.Iterable[str] = (),
    ) -> list[MSBEntry]:
        """Lists of entries can include names of entries, if unique, or the actual `MSBEntry` instances."""
        if not entries:
            return []
        resolved = []
        for entry in entries:
            if isinstance(entry, str):
                resolved.append(self.find_entry_by_name(entry, supertypes, subtypes))
            elif isinstance(entry, MSBEntry):
                resolved.append(entry)
            else:
                raise TypeError(f"Invalid MSB entry specifier: {entry}. Must be a (unique) entry name or `MSBEntry`.")
        return resolved

    def get_repeated_entity_ids(self) -> dict[str, list[MSBEntry]]:
        """Scans all entries for repeated `entity_id` fields *per supertype*.

        Repeated IDs across different supertypes will be ignored.
        """
        repeats = {}
        for supertype_name in MSB_ENTRY_SUPERTYPES[1:]:  # not 'MODEL_PARAM_ST'
            supertype_list = self.get_supertype_list(supertype_name)
            entity_ids = set()
            repeated_entries = []  # type: list[MSBEntry]
            for entry in supertype_list:
                entity_id = entry.get_entity_id()
                if entity_id is None or entity_id <= 0:  # some subtypes have 'null' ID zero (e.g. environment events)
                    continue
                if entity_id in entity_ids:
                    repeated_entries.append(entry)
                else:
                    entity_ids.add(entity_id)
            repeats[supertype_name] = repeated_entries
        return repeats

    def get_supertype_entity_id_dict(self, supertype_name: str) -> dict[int, MSBEntry]:
        """Get a dictionary mapping entity IDs to `MSBEntry` instances for the given supertype.

        If multiple `MSBEntry` instances are found for a given ID, a warning is logged, and only the *first* one found
        is used (which matches game engine behavior).

        Analogous to the subtype-only method in `MSBEntryList`.
        """
        supertype_list = self.get_supertype_list(supertype_name)
        entries_by_id = {}
        for entry in supertype_list:
            entity_id = entry.get_entity_id()
            if entity_id is None or entity_id <= 0:
                continue  # ignore unavailable or null ID
            if entity_id in entries_by_id:
                _LOGGER.warning(f"Found multiple entries for entity ID {entity_id}. Only using first.")
            else:
                entries_by_id[entity_id] = entry
        return entries_by_id

    def get_supertype_entity_id_name_dict(self, supertype_name: str) -> dict[int, str]:
        """As above, but values are just entry names instead of the entries themselves."""
        entries_by_id = self.get_supertype_entity_id_dict(supertype_name)
        return {entity_id: entry.name for entity_id, entry in entries_by_id.items()}

    def find_entry_by_entity_id(self, entity_id: int, allow_multiple=True) -> MSBEntry | None:
        """Search ALL entries for the given entity ID and return that `MSBEntry` (or `None` if not found).

        If multiple entries with the same (non-default) ID are found, an error will be raised unless
        `allow_multiple=True`.
        """
        if entity_id <= 0:
            raise ValueError(f"Cannot find MSB entry using default entity ID value {entity_id}.")
        results = []
        for supertype_name in MSB_ENTRY_SUPERTYPES[1:]:
            supertype_list = self.get_supertype_list(supertype_name)
            results.extend([entry for entry in supertype_list if entry.get_entity_id() == entity_id])
        if not results:
            raise KeyError(f"Could not find an entry with entity ID {entity_id} in MSB.")
        elif len(results) > 1:
            if allow_multiple:
                _LOGGER.warning(
                    f"Found multiple entries with entity ID {entity_id} in MSB. This should be fixed. "
                    f"Returning first one only."
                )
            else:
                raise ValueError(f"Found multiple entries with entity ID {entity_id} in MSB. This must be fixed.")
        return results[0]

    def clear_all(self):
        """Clear all entry subtype lists."""
        for entry_list in self.get_all_subtype_lists():
            entry_list.clear()

    def __iter__(self):
        """Iterate over all subtype lists."""
        return iter(self.get_all_subtype_lists())

    def write_entities_module(
        self,
        module_path: str | Path = None,
        area_id: int = None,
        block_id: int = None,
        # TODO: cc_id and dd_id for Elden Ring
        append_to_module: str = ""
    ):
        """Generates a '{mXX_YY}_entities.py' file with entity IDs for import into EVS script.

        If `append_to_module` text is given, all map entities will be appended to it.
        """
        if module_path is None:
            if self.path is None:
                raise ValueError("Cannot auto-detect MSB entities `module_path` (MSB path not known).")
            module_path = self.path.parent / f"{self.path.name.split('.')[0]}_entities.py"

        module_path.parent.mkdir(parents=True, exist_ok=True)

        auto_map_range_start = None
        if area_id is None and block_id is None:
            if self.path:
                map_name_match = MAP_NAME_RE.match(self.path.name)
                if map_name_match:
                    area_id, block_id = map(int, map_name_match.group(1, 2))
                    auto_map_range_start = area_id * 100000 + block_id * 10000
                else:
                    _LOGGER.warning(
                        f"Could not auto-detect map area and block (cannot parse from MSB path: {self.path}). "
                        "Auto-enumerator functions will be commented out; replace the {MAP_RANGE_START} string in each "
                        "one and uncomment to use."
                    )
            else:
                _LOGGER.warning(
                    "Could not auto-detect map area and block (MSB path not known). Auto-enumerator functions will be"
                    "commented out; replace the {MAP_RANGE_START} string in each one and uncomment to use."
                )
        elif area_id is not None and block_id is not None:
            auto_map_range_start = area_id * 100000 + block_id * 10000
        else:
            raise ValueError("Both `area_id` and `block_id` must be given, or neither for automatic detection.")

        trailing_digit_re = re.compile(r"(.*?)(\d+)")

        def sort_key(key_value) -> tuple[str, int]:
            """Sort trailing digits properly."""
            _, value_ = key_value
            if match := trailing_digit_re.match(value_.name):
                return match.group(1), int(match.group(2))
            return value_.name, 0

        module_path = Path(module_path)

        game_types_import = f"from soulstruct.{self.get_game().submodule_name}.game_types import *\n"
        if append_to_module:
            if game_types_import not in append_to_module:
                # Add game type start import to module. (Very rare that it wouldn't already be there.)
                first_class_def_index = append_to_module.find("\nclass")
                if first_class_def_index != -1:
                    append_to_module = append_to_module.replace("\nclass", game_types_import + "\n\nclass", 1)
                else:
                    append_to_module += game_types_import
            module_text = append_to_module.rstrip("\n") + "\n"
        else:
            module_text = game_types_import

        for subtype_name, subtype_game_type in self.ENTITY_GAME_TYPES.items():
            class_name = subtype_game_type.get_msb_entry_type_subtype(pluralized_subtype=True)[1]
            class_text = ""
            subtype_list = getattr(self, subtype_name)
            entity_id_dict = subtype_list.get_entity_id_dict()
            sorted_entity_id_dict = {
                k: v for k, v in sorted(entity_id_dict.items(), key=sort_key)
            }
            for entity_id, entry in sorted_entity_id_dict.items():
                # name = entry.name.replace(" ", "_")
                try:
                    name = entry.name.encode("utf-8").decode("ascii")
                except UnicodeDecodeError:
                    class_text += f"    # TODO: Non-ASCII name characters.\n    # {entry.name} = {entity_id}"
                else:
                    if not PY_NAME_RE.match(name):
                        class_text += f"    # TODO: Invalid variable name.\n    # {entry.name} = {entity_id}"
                    else:
                        class_text += f"    {name} = {entity_id}"
                if entry.description:
                    class_text += f"  # {entry.description}"
                class_text += "\n"
            if class_text:
                class_def = f"\n\nclass {class_name}({subtype_game_type.__name__}):\n"
                class_def += f"    \"\"\"`{subtype_game_type.__name__}` entity IDs for MSB and EVS use.\"\"\"\n\n"
                auto_lines = [
                    "    # noinspection PyMethodParameters",
                    "    def _generate_next_value_(name, _, count, __):",
                    f"        return {subtype_game_type.__name__}.auto_generate(count, {{MAP_RANGE_START}})",
                ]
                if auto_map_range_start is None:
                    auto_lines = ["    # " + line[4:] for line in auto_lines]
                else:
                    auto_lines[-1] = auto_lines[-1].format(MAP_RANGE_START=auto_map_range_start)
                class_def += "\n".join(auto_lines) + "\n\n"
                class_text = class_def + class_text
                module_text += class_text

        with module_path.open("w", encoding="utf-8") as f:
            f.write(module_text)

    # TODO: Methods to import entity IDs from module by matching names, and import names from module by matching entity
    #  IDs (e.g. once you fix exported Japanese names).

    def has_c0000_model(self) -> bool:
        """Common check for character/player model c0000, which should be in every MSB (in every game)."""
        character_models = getattr(self, "character_models")  # type: MSBEntryList
        try:
            character_models.find_entry_name("c0000")
        except KeyError:
            player_models = getattr(self, "player_models")
            try:
                player_models.find_entry_name("c0000")
            except KeyError:
                return False
        return True

    @classmethod
    def get_display_type_dict(cls) -> dict[str, tuple[BaseMSBSubtype]]:
        """Return a nested dictionary mapping MSB type names (in typical display order) to tuples of subtype enums."""
        display_dict = {}  # type: dict[str, tuple[BaseMSBSubtype]]
        for supertype_name, subtypes_info in cls.MSB_ENTRY_SUBTYPES.items():
            display_dict[supertype_name] = tuple(info.subtype_enum for info in subtypes_info.values())
        return {
            "Parts": display_dict["PARTS_PARAM_ST"],
            "Regions": display_dict["POINT_PARAM_ST"],
            "Events": display_dict["EVENT_PARAM_ST"],
            "Models": display_dict["MODELS_PARAM_ST"],
        }

    def __getitem__(self, subtype_list_name: str) -> MSBEntryList:
        """Retrieve entry subtype list by name, e.g. "characters" or "map_piece_models"."""
        subtype_list_name = subtype_list_name.lower()
        return getattr(self, subtype_list_name)

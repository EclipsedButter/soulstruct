from __future__ import annotations

__all__ = [
    "FLVER0",
]

import logging
import typing as tp
from dataclasses import dataclass, field

from soulstruct.utilities.binary import *
from soulstruct.utilities.misc import IDList
from soulstruct.utilities.maths import Vector3
from soulstruct.base.models.base.core import BaseFLVER
from soulstruct.base.models.base.bone import FLVERBone
from soulstruct.base.models.base.dummy import Dummy
from soulstruct.base.models.base.version import FLVERVersion
from .submesh import Submesh
from .material import Material
from .mesh_tools import MergedMesh
from .vertex_array_layout import VertexArrayLayout

_LOGGER = logging.getLogger("Soulstruct")


@dataclass(slots=True, repr=False)
class FLVER0(BaseFLVER[Submesh]):
    """Old FLVER format used in Demon's Souls and other older (pre-DS1) games."""

    @dataclass(slots=True)
    class STRUCT(BinaryStruct):
        _file_type: bytes = field(init=False, **BinaryString(6, asserted=b"FLVER"))
        endian: bytes = field(**BinaryString(2, rstrip_null=False, asserted=[b"L\0", b"B\0"]))
        version: FLVERVersion = field(**Binary(int))
        vertex_data_offset: int
        vertex_data_size: int
        dummy_count: int
        material_count: int
        bone_count: int
        mesh_count: int
        vertex_array_count: int
        bounding_box_min: Vector3
        bounding_box_max: Vector3
        true_face_count: int  # not including motion blur meshes or degenerate faces
        total_face_count: int
        vertex_indices_size: byte = field(**Binary(asserted=[16, 32]))  # no 'local' zero option in FLVER0
        unicode: bool
        unk_x4a: byte  # bool in `FLVER`
        unk_x4b: byte  # pad in `FLVER`
        unk_x4c: int
        _pad0: bytes = field(init=False, **BinaryPad(12))  # no face set, array layout, or texture counts
        unk_x5c: byte
        _pad2: bytes = field(init=False, **BinaryPad(3))  # alignment after `unk_x5c`
        _pad3: bytes = field(init=False, **BinaryPad(32))

    # Defaults (possibly constants) observed for DeS Characters and Map Pieces:
    unk_x4a: int = 1
    unk_x4b: int = 0
    unk_x4c: int = 65535
    unk_x5c: int = 0

    submeshes: list[Submesh] = field(default_factory=list)  # override

    @classmethod
    def from_reader(cls, reader: BinaryReader) -> tp.Self:
        """Much simpler than `FLVER` with all the missing elements."""
        byte_order = ByteOrder.from_reader_peek(reader, 2, 6, b"B\0", b"L\0")
        reader.default_byte_order = byte_order  # applies to all FLVER structs (manually passed to `VertexArray`)
        header = cls.STRUCT.from_bytes(reader)
        big_endian = header.endian == b"B\0"
        encoding = reader.default_byte_order.get_utf_16_encoding() if header.unicode else "shift_jis_2004"

        dummies = [Dummy.from_flver_reader(reader, header.version) for _ in range(header.dummy_count)]
        materials = [Material.from_flver_reader(reader, encoding, header.version) for _ in range(header.material_count)]

        bones = IDList()  # type: IDList[FLVERBone]
        for _ in range(header.bone_count):
            bone = FLVERBone.from_flver_reader(reader, encoding=encoding)
            bones.append(bone)
        for bone in bones:
            bone.set_bones(bones)

        submeshes = [
            Submesh.from_flver_reader(
                reader=reader,
                vertex_index_size=header.vertex_indices_size,
                vertex_data_offset=header.vertex_data_offset,
                materials=materials,
                big_endian=big_endian,
            ) for _ in range(header.mesh_count)
        ]
        for i, submesh in enumerate(submeshes):
            submesh.index = i

        return cls(
            big_endian=big_endian,
            version=FLVERVersion(header.version),
            unicode=header.unicode,
            unk_x4a=header.unk_x4a,
            unk_x4b=header.unk_x4b,
            unk_x4c=header.unk_x4c,
            unk_x5c=header.unk_x5c,
            bounding_box_min=header.bounding_box_min,
            bounding_box_max=header.bounding_box_max,
            dummies=dummies,
            bones=bones,
            submeshes=submeshes,
        )

    def to_writer(self) -> BinaryWriter:

        byte_order = ByteOrder.BigEndian if self.big_endian else ByteOrder.LittleEndian
        encoding = byte_order.get_utf_16_encoding() if self.unicode else "shift_jis_2004"

        true_face_count = 0
        total_face_count = 0
        for submesh in self.submeshes:
            if len(submesh.face_sets) != 1:
                raise ValueError("Each FLVER0 Submesh must have exactly one FaceSet.")
            face_set = submesh.face_sets[0]
            allow_primitive_restarts = len(submesh.vertices) < 0xFFFF  # max unsigned short value
            face_set_true_count, face_set_total_count = face_set.get_face_counts(allow_primitive_restarts)
            true_face_count += face_set_true_count
            total_face_count += face_set_total_count

        # We only support 16 or 32-bit vertices in FLVER0. If any Submesh needs 32-bit vertices, all use them.
        vertex_indices_size = 16
        for submesh in self.submeshes:
            if submesh.face_sets[0].needs_32bit_indices():
                vertex_indices_size = 32
                break  # no point checking further

        header = self.STRUCT.from_object(
            self,
            byte_order=byte_order,
            endian=b"B\0" if self.big_endian else b"L\0",
            vertex_data_offset=RESERVED,
            vertex_data_size=RESERVED,
            dummy_count=len(self.dummies),
            material_count=RESERVED,  # unique Materials collected below
            bone_count=len(self.bones),
            mesh_count=len(self.submeshes),
            vertex_array_count=len(self.submeshes),  # each submesh has one vertex array
            true_face_count=true_face_count,
            total_face_count=total_face_count,
            vertex_indices_size=vertex_indices_size,
        )

        writer = header.to_writer(reserve_obj=self)

        for dummy in self.dummies:
            dummy.to_flver_writer(writer, self.version)

        materials_to_pack = []  # type: list[Material]  # unique materials to actually pack to FLVER
        hashed_material_indices = {}  # type: dict[int, int]  # maps material hashes to `materials_to_pack` indices
        hashed_material_layouts_to_pack = {}  # type: dict[int, list[VertexArrayLayout]]
        hashed_material_hashed_layout_indices = {}  # type: dict[int, dict[int, int]]
        submesh_material_indices = []  # type: list[int]
        submesh_material_layout_indices = []  # type: list[int]

        for submesh in self.submeshes:
            material = submesh.material
            material_hash = hash(material)  # includes name!
            if material_hash in hashed_material_indices:
                # Identical material already used by a previous Submesh. Reuse it.
                submesh_material_index = hashed_material_indices[material_hash]
            else:
                # New material.
                submesh_material_index = hashed_material_indices[material_hash] = len(materials_to_pack)
                materials_to_pack.append(material)

            submesh_material_indices.append(submesh_material_index)
            layouts_to_pack = hashed_material_layouts_to_pack.setdefault(material_hash, [])
            hashed_layout_indices = hashed_material_hashed_layout_indices.setdefault(material_hash, {})

            layout = submesh.vertex_arrays[0].layout
            layout_hash = hash(tuple((data_type.type_int, data_type.format_enum) for data_type in layout))
            if layout_hash in hashed_layout_indices:
                # Identical layout already used by a Submesh that uses this Material. Reuse it.
                material_layout_index = hashed_layout_indices[layout_hash]
            else:
                # New layout (for this Material).
                material_layout_index = hashed_layout_indices[layout_hash] = len(layouts_to_pack)
                layouts_to_pack.append(layout)
            submesh_material_layout_indices.append(material_layout_index)

        writer.fill("material_count", len(materials_to_pack), obj=self)

        # Pack materials.
        for material in materials_to_pack:
            material.to_flver_writer(writer)

        # Pack bones.
        for bone in self.bones:
            bone.set_bone_indices(self.bones)
            bone.to_flver_writer(writer, self.bones)

        # Pack submesh headers.
        for submesh, material_index in zip(self.submeshes, submesh_material_indices):
            submesh.to_flver_writer(writer, vertex_indices_size, material_index)

        # Pack material data.
        for material in materials_to_pack:
            material.pack_data(writer, encoding)

        # Pack bone names.
        for bone in self.bones:
            bone.pack_name(writer, encoding=encoding)

        # Pack submesh vertex array headers.
        for submesh, material_layout_index in zip(self.submeshes, submesh_material_layout_indices):
            # Unlike `FLVER`, we use a Submesh method here, because the list of headers has some initial fields.
            submesh.pack_vertex_array_header(writer, material_layout_index)

        writer.pad_align(32)
        vertex_data_offset = writer.position
        writer.fill("vertex_data_offset", vertex_data_offset, obj=self)

        for submesh in self.submeshes:
            indices_offset = writer.position - vertex_data_offset
            submesh.pack_vertex_indices(writer, vertex_indices_size, indices_offset)
            writer.pad_align(32)
            array_offset = writer.position - vertex_data_offset
            submesh.vertex_arrays[0].pack_array(
                writer,
                array_offset=array_offset,
                uv_factor=1024 if self.big_endian else 2048,
                big_endian=self.big_endian,
            )
            # Single vertex array offset (relative to FLVER vertex data start) is also written to Submesh header.
            writer.fill("vertex_array_data_offset", array_offset, obj=submesh)
            writer.pad_align(32)

        writer.fill("vertex_data_size", writer.position - vertex_data_offset, obj=self)

        return writer

    def to_merged_mesh(
        self,
        submesh_material_indices: tp.Sequence[int] = None,
        material_uv_layer_names: tp.Sequence[tp.Sequence[str]] = None,
        merge_vertices=True,
    ) -> MergedMesh:
        """Return a `BaseMergedMesh` object that combines all submeshes of this FLVER into a single mesh."""
        return MergedMesh.from_flver(self, submesh_material_indices, material_uv_layer_names, merge_vertices)

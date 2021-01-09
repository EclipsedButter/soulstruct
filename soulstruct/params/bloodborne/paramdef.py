from __future__ import annotations

__all__ = ["ParamDefField", "ParamDef", "ParamDefBND"]

import typing as tp

from soulstruct.params.base.paramdef import (
    ParamDefField as _BaseParamDefField,
    ParamDef as _BaseParamDef,
    ParamDefBND as _BaseParamDefBND,
)
from soulstruct.utilities.binary_struct import BinaryStruct

from .display_info import get_param_info, get_param_info_field

if tp.TYPE_CHECKING:
    from soulstruct.params.base.param import ParamRow

_BUNDLED = None


class ParamDefField(_BaseParamDefField):

    STRUCT = BinaryStruct(
        ("debug_name", "64u"),
        ("debug_type", "8j"),
        ("debug_format", "8j"),  # %i, %u, %d, etc.
        ("default", "f"),
        ("minimum", "f"),
        ("maximum", "f"),
        ("increment", "f"),
        ("debug_display", "i"),
        ("size", "i"),
        ("description_offset", "q"),
        ("internal_type", "32j"),  # could be an enum name (see params.enums)
        ("name", "32j"),
        ("sort_id", "i"),
        "28x",
    )

    def get_display_info(self, entry: ParamRow):
        try:
            field_info = get_param_info_field(self.param_name, self.name)
        except ValueError:
            raise ValueError(f"No display information given for field '{self.name}'.")
        return field_info(entry)


class ParamDef(_BaseParamDef):
    BYTE_ORDER = "<"
    STRUCT = BinaryStruct(
        ("size", "i"),
        ("header_size", "H", 255),
        ("data_version", "H"),
        ("field_count", "H"),
        ("field_size", "H", 208),
        "4x",
        ("param_name_offset", "q"),
        "20x",
        ("big_endian", "B"),
        ("unicode", "?"),
        ("format_version", "h", 201),
        ("unk1", "q", 56),
    )
    FIELD_CLASS = ParamDefField

    @property
    def param_info(self):
        try:
            return get_param_info(self.param_type)
        except KeyError:
            # This param has no extra information.
            return None


class ParamDefBND(_BaseParamDefBND):
    PARAMDEF_CLASS = ParamDef


def GET_BUNDLED() -> ParamDefBND:
    global _BUNDLED
    if _BUNDLED is None:
        _BUNDLED = ParamDefBND()
    return _BUNDLED

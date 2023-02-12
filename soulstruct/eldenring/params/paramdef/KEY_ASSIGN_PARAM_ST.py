from __future__ import annotations

__all__ = ["KEY_ASSIGN_PARAM_ST"]

from dataclasses import dataclass

from soulstruct.base.params.utils import *
from soulstruct.eldenring.game_types import *
from soulstruct.eldenring.params.enums import *
from soulstruct.utilities.binary import *


# noinspection PyDataclass
@dataclass(slots=True)
class KEY_ASSIGN_PARAM_ST(ParamRow):
    PadKeyId: int = ParamField(
        int, "padKeyId", default=-1,
        tooltip="TOOLTIP-TODO",
    )
    KeyboardModifyKey: int = ParamField(
        int, "keyboardModifyKey", default=0,
        tooltip="TOOLTIP-TODO",
    )
    KeyboardKeyId: int = ParamField(
        int, "keyboardKeyId", default=-1,
        tooltip="TOOLTIP-TODO",
    )
    MouseModifyKey: int = ParamField(
        int, "mouseModifyKey", default=0,
        tooltip="TOOLTIP-TODO",
    )
    MouseKeyId: int = ParamField(
        int, "mouseKeyId", default=0,
        tooltip="TOOLTIP-TODO",
    )
    _Pad0: bytes = ParamPad(12, "reserved[12]")

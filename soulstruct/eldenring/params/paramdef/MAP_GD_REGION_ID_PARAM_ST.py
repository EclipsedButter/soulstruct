from __future__ import annotations

__all__ = ["MAP_GD_REGION_ID_PARAM_ST"]

from dataclasses import dataclass

from soulstruct.base.params.utils import *
from soulstruct.eldenring.game_types import *
from soulstruct.eldenring.params.enums import *
from soulstruct.utilities.binary import *


# noinspection PyDataclass
@dataclass(slots=True)
class MAP_GD_REGION_ID_PARAM_ST(ParamRowData):
    DisableParamNT: int = ParamField(
        byte, "disableParam_NT:1", default=0,
        tooltip="TOOLTIP-TODO",
    )
    _Pad0: bytes = ParamPad(1, "disableParamReserve1:7")
    _Pad1: bytes = ParamPad(3, "disableParamReserve2[3]")
    MapRegionId: int = ParamField(
        uint, "mapRegionId", default=0,
        tooltip="TOOLTIP-TODO",
    )
    _Pad2: bytes = ParamPad(24, "Reserve[24]")

from __future__ import annotations

__all__ = ["CS_LIGHTING_QUALITY_DETAIL"]

from dataclasses import dataclass

from soulstruct.base.params.utils import *
from soulstruct.eldenring.game_types import *
from soulstruct.eldenring.params.enums import *
from soulstruct.utilities.binary import *


# noinspection PyDataclass
@dataclass(slots=True)
class CS_LIGHTING_QUALITY_DETAIL(ParamRow):
    LocalLightDistFactor: float = ParamField(
        float, "localLightDistFactor", default=0,
        tooltip="TOOLTIP-TODO",
    )
    LocalLightShadowEnabled: int = ParamField(
        byte, "localLightShadowEnabled", default=1,
        tooltip="TOOLTIP-TODO",
    )
    ForwardPassLightingEnabled: int = ParamField(
        byte, "forwardPassLightingEnabled", default=1,
        tooltip="TOOLTIP-TODO",
    )
    LocalLightShadowSpecLevelMax: int = ParamField(
        byte, "localLightShadowSpecLevelMax", default=1,
        tooltip="TOOLTIP-TODO",
    )
    _Pad0: bytes = ParamPad(1, "dmy[1]")

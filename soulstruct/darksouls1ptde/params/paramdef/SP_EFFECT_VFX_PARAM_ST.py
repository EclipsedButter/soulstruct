from __future__ import annotations

__all__ = ["SP_EFFECT_VFX_PARAM_ST"]

from dataclasses import dataclass

from soulstruct.base.params.utils import *
from soulstruct.darksouls1ptde.game_types import *
from soulstruct.darksouls1ptde.params.enums import *
from soulstruct.utilities.binary import *


# noinspection PyDataclass
@dataclass(slots=True)
class SP_EFFECT_VFX_PARAM_ST(ParamRow):
    OngoingVisualEffect: VisualEffect = ParamField(
        int, "midstSfxId", default=-1,
        tooltip="Ongoing visual effect for special effect. -1 is no effect.",
    )
    OngoingSoundEffect: SFXSound = ParamField(
        int, "midstSeId", default=-1,
        tooltip="Ongoing sound effect for special effect. -1 is no effect.",
    )
    InitialVisualEffect: VisualEffect = ParamField(
        int, "initSfxId", default=-1,
        tooltip="One-off visual effect when special effect begins. -1 is no effect.",
    )
    InitialSoundEffect: SFXSound = ParamField(
        int, "initSeId", default=-1, hide=True,
        tooltip="One-off sound effect when special effect begins. -1 is no effect. (Does not appear to work.)",
    )
    FinishVisualEffect: VisualEffect = ParamField(
        int, "finishSfxId", default=-1,
        tooltip="One-off visual effect when special effect ends. -1 is no effect.",
    )
    FinishSoundEffect: SFXSound = ParamField(
        int, "finishSeId", default=-1, hide=True,
        tooltip="One-off sound effect when special effect ends. -1 is no effect. (Does not appear to work.)",
    )
    HideStartDistance: float = ParamField(
        float, "camouflageBeginDist", default=-1.0,
        tooltip="Closest distance at which effect is disabled.",
    )
    HideEndDistance: float = ParamField(
        float, "camouflageEndDist", default=-1.0,
        tooltip="Furthest distance at which effect is disabled.",
    )
    TransformationArmorID: ArmorParam = ParamField(
        int, "transformProtectorId", default=-1,
        tooltip="Transformation armor ID. Unknown effect. -1 is no armor.",
    )
    OngoingModelPoint: int = ParamField(
        short, "midstDmyId", default=-1,
        tooltip="Model point where ongoing effects are centered. -1 is model root.",
    )
    InitialModelPoint: int = ParamField(
        short, "initDmyId", default=-1,
        tooltip="Model point where initial effect is centered. -1 is model root.",
    )
    FinishModelPoint: int = ParamField(
        short, "finishDmyId", default=-1,
        tooltip="Model point where finish effect is centered. -1 is model root.",
    )
    EffectType: SP_EFFECT_VFX_EFFECT_TYPE = ParamField(
        byte, "effectType", default=0,
        tooltip="Type of effect. Enum not yet mapped.",
    )
    WeaponEnchantmentSoulParam: SP_EFFECT_VFX_SOUL_PARAM_TYPE = ParamField(
        byte, "soulParamIdForWepEnchant", default=0,
        tooltip="Internal description: 'Soul Param ID for weapon enchantment.' Enum not yet mapped.",
    )
    PlaybackCategory: SP_EFFECT_VFX_PLAYCATEGORY = ParamField(
        byte, "playCategory", default=0,
        tooltip="Only one effect in each category can be active at once (determined by PlaybackPriority).",
    )
    PlaybackPriority: int = ParamField(
        byte, "playPriority", default=0,
        tooltip="Only the lowest-numbered-priority effect in each PlaybackCategory will be active at once.",
    )
    LargeEffectExists: bool = ParamField(
        byte, "existEffectForLarge:1", bit_count=1, default=False,
        tooltip="Indicates if a large version of the effect exists.",
    )
    SoulEffectExists: bool = ParamField(
        byte, "existEffectForSoul:1", bit_count=1, default=False,
        tooltip="Indicates if a 'soul version' of the effect exists.",
    )
    InvisibleWhenHidden: bool = ParamField(
        byte, "effectInvisibleAtCamouflage:1", bit_count=1, default=False,
        tooltip="Indicates if the effect should be invisible when hidden (unclear exactly what this means).",
    )
    HidingActive: bool = ParamField(
        byte, "useCamouflage:1", bit_count=1, default=False,
        tooltip="I believe this determines if the hiding range fields are actually used.",
    )
    InvisibleWhenFriendHidden: bool = ParamField(
        byte, "invisibleAtFriendCamouflage:1", bit_count=1, default=False,
        tooltip="Unclear.",
    )
    AddMapAreaBlockOffset: bool = ParamField(
        byte, "addMapAreaBlockOffset:1", bit_count=1, default=False,
        tooltip="If enabled, the three-digit area/block number for the current map will be added to all effect IDs "
                "(e.g. m13_02 -> adds 132).",
    )
    HalfHiddenOnly: bool = ParamField(
        byte, "halfCamouflage:1", bit_count=1, default=False,
        tooltip="If enabled, effects are made semi-transparent rather than fully hidden.",
    )
    ArmorTransformationIsFullBody: bool = ParamField(
        byte, "isFullBodyTransformProtectorId:1", bit_count=1, default=False,
        tooltip="Indicates whether the armor transformation should be applied to the whole body.",
    )
    HideWeapon: bool = ParamField(
        byte, "isInvisibleWeapon:1", bit_count=1, default=False,
        tooltip="Weapon is invisible if enabled.",
    )
    IsSilent: bool = ParamField(
        byte, "isSilence:1", bit_count=1, default=False,
        tooltip="Movement noises are silenced if enabled.",
    )
    _BitPad0: int = ParamBitPad(byte, "pad_1:6", bit_count=6)
    _Pad0: bytes = ParamPad(16, "pad[16]")

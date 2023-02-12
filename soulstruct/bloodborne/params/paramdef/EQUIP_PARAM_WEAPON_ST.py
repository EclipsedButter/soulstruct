from __future__ import annotations

__all__ = ["EQUIP_PARAM_WEAPON_ST"]

from dataclasses import dataclass

from soulstruct.base.params.utils import *
from soulstruct.bloodborne.game_types import *
from soulstruct.bloodborne.params.enums import *
from soulstruct.utilities.binary import *


# noinspection PyDataclass
@dataclass(slots=True)
class EQUIP_PARAM_WEAPON_ST(ParamRow):
    BehaviorVariationID: int = ParamField(
        int, "behaviorVariationId", default=0,
        tooltip="Multiplied by 1000 and added to player behavior lookups (hitboxes, bullets) triggered by TAE.",
    )
    SortIndex: int = ParamField(
        int, "sortId", default=0,
        tooltip="Index for automatic inventory sorting.",
    )
    GhostWeaponReplacement: WeaponParam = ParamField(
        uint, "wanderingEquipId", default=0,
        tooltip="Weapon replacement for ghosts.",
    )
    Weight: float = ParamField(
        float, "weight", default=1.0,
        tooltip="Weight of weapon.",
    )
    WeightRatio: float = ParamField(
        float, "weaponWeightRate", default=0.0,
        tooltip="Unknown effect. Value is about evenly split between 0 and 1 across weapons, with no obvious pattern.",
    )
    RepairCost: int = ParamField(
        int, "fixPrice", default=0,
        tooltip="Amount of souls required to repair weapon fully. Actual repair cost is this multiplied by current "
                "durability over max durability.",
    )
    BasicCost: int = ParamField(
        int, "basicPrice", default=0, hide=True,
        tooltip="Unknown purpose, and unused.",
    )
    FramptSellValue: int = ParamField(
        int, "sellValue", default=0,
        tooltip="Amount of souls received when fed to Frampt. (Set to -1 to prevent it from being sold.",
    )
    StrengthScaling: float = ParamField(
        float, "correctStrength", default=0.0,
        tooltip="Amount of attack power gained from strength. (I believe this is the percentage of the player's "
                "strength to add to the weapon's attack power, but it also depends on ScalingFormulaType below.)",
    )
    DexterityScaling: float = ParamField(
        float, "correctAgility", default=0.0,
        tooltip="Amount of attack power gained from dexterity. (I believe this is the percentage of the player's "
                "dexterity to add to the weapon's attack power, but it also depends on ScalingFormulaType below.).",
    )
    IntelligenceScaling: float = ParamField(
        float, "correctMagic", default=0.0,
        tooltip="Amount of attack power gained from intelligence. (I believe this is the percentage of the player's "
                "intelligence to add to the weapon's attack power, but it also depends on ScalingFormulaType below.)",
    )
    FaithScaling: float = ParamField(
        float, "correctFaith", default=0.0,
        tooltip="Amount of attack power gained from faith. (I believe this is the percentage of the player's faith to "
                "add to the weapon's attack power, but it also depends on ScalingFormulaType below.)",
    )
    PhysicalGuardPercentage: float = ParamField(
        float, "physGuardCutRate", default=0.0,
        tooltip="Percentage of physical damage prevented when guarding with this weapon.",
    )
    MagicGuardPercentage: float = ParamField(
        float, "magGuardCutRate", default=0.0,
        tooltip="Percentage of magic damage prevented when guarding with this weapon.",
    )
    FireGuardPercentage: float = ParamField(
        float, "fireGuardCutRate", default=0.0,
        tooltip="Percentage of fire damage prevented when guarding with this weapon.",
    )
    LightningGuardPercentage: float = ParamField(
        float, "thunGuardCutRate", default=0.0,
        tooltip="Percentage of lightning damage prevented when guarding with this weapon.",
    )
    SpecialEffectOnHit0: SpecialEffectParam = ParamField(
        int, "spEffectBehaviorId0", default=-1,
        tooltip="Special effect applied to struck target (slot 0).",
    )
    SpecialEffectOnHit1: SpecialEffectParam = ParamField(
        int, "spEffectBehaviorId1", default=-1,
        tooltip="Special effect applied to struck target (slot 1).",
    )
    SpecialEffectOnHit2: SpecialEffectParam = ParamField(
        int, "spEffectBehaviorId2", default=-1,
        tooltip="Special effect applied to struck target (slot 2).",
    )
    EquippedSpecialEffect0: SpecialEffectParam = ParamField(
        int, "residentSpEffectId", default=-1,
        tooltip="Special effect granted to character with weapon equipped (slot 0).",
    )
    EquippedSpecialEffect1: SpecialEffectParam = ParamField(
        int, "residentSpEffectId1", default=-1,
        tooltip="Special effect granted to character with weapon equipped (slot 1).",
    )
    EquippedSpecialEffect2: SpecialEffectParam = ParamField(
        int, "residentSpEffectId2", default=-1,
        tooltip="Special effect granted to character with weapon equipped (slot 2).",
    )
    UpgradeMaterialID: UpgradeMaterialParam = ParamField(
        int, "materialSetId", default=-1,
        tooltip="Upgrade Material parameter that sets costs for weapon reinforcement.",
    )
    UpgradeOrigin0: WeaponParam = ParamField(
        int, "originEquipWep", default=-1,
        tooltip="Origin armor for level 0 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin1: WeaponParam = ParamField(
        int, "originEquipWep1", default=-1,
        tooltip="Origin armor for level 1 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin2: WeaponParam = ParamField(
        int, "originEquipWep2", default=-1,
        tooltip="Origin armor for level 2 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin3: WeaponParam = ParamField(
        int, "originEquipWep3", default=-1,
        tooltip="Origin armor for level 3 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin4: WeaponParam = ParamField(
        int, "originEquipWep4", default=-1,
        tooltip="Origin armor for level 4 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin5: WeaponParam = ParamField(
        int, "originEquipWep5", default=-1,
        tooltip="Origin armor for level 5 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin6: WeaponParam = ParamField(
        int, "originEquipWep6", default=-1,
        tooltip="Origin armor for level 6 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin7: WeaponParam = ParamField(
        int, "originEquipWep7", default=-1,
        tooltip="Origin armor for level 7 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin8: WeaponParam = ParamField(
        int, "originEquipWep8", default=-1,
        tooltip="Origin armor for level 8 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin9: WeaponParam = ParamField(
        int, "originEquipWep9", default=-1,
        tooltip="Origin armor for level 9 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin10: WeaponParam = ParamField(
        int, "originEquipWep10", default=-1,
        tooltip="Origin armor for level 10 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin11: WeaponParam = ParamField(
        int, "originEquipWep11", default=-1,
        tooltip="Origin armor for level 11 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin12: WeaponParam = ParamField(
        int, "originEquipWep12", default=-1,
        tooltip="Origin armor for level 12 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin13: WeaponParam = ParamField(
        int, "originEquipWep13", default=-1,
        tooltip="Origin armor for level 13 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin14: WeaponParam = ParamField(
        int, "originEquipWep14", default=-1,
        tooltip="Origin armor for level 14 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    UpgradeOrigin15: WeaponParam = ParamField(
        int, "originEquipWep15", default=-1,
        tooltip="Origin armor for level 15 of this weapon (i.e. what you receive when a blacksmith removes upgrades). "
                "If -1, the weapon cannot be reverted. Otherwise, it will appear in each blacksmith's reversion menu.",
    )
    DamageAgainstDemonsMultiplier: float = ParamField(
        float, "antiDemonDamageRate", default=1.0,
        tooltip="Multiplier applied to damage dealt against demons with this weapon.",
    )
    WeakToDivineDamageMultiplier: float = ParamField(
        float, "antSaintDamageRate", default=1.0,
        tooltip="Multiplier applied to damage dealt against enemies weak to divine (e.g. skeletons) with this weapon.",
    )
    GodDamageMultiplier: float = ParamField(
        float, "antWeakA_DamageRate", default=1.0,
        tooltip="Multiplier applied to damage dealt against Gods and Goddesses with this weapon.",
    )
    AbyssDamageMultiplier: float = ParamField(
        float, "antWeakB_DamageRate", default=1.0,
        tooltip="Multiplier applied to damage dealt against enemies from the Abyss with this weapon.",
    )
    LevelSyncCorrectID: int = ParamField(
        short, "levelSyncCorrectId", default=-1,
        tooltip="TODO",
    )
    _Pad0: bytes = ParamPad(2, "pad[2]")
    VagrantBonusEnemyDropItemLot: ItemLotParam = ParamField(
        int, "vagrantBonusEneDropItemLotId", default=0, hide=True,
        tooltip="TODO",
    )
    VagrantItemEnemyDropItemLot: ItemLotParam = ParamField(
        int, "vagrantItemEneDropItemLotId", default=0, hide=True,
        tooltip="TODO",
    )
    WeaponModel: int = ParamField(
        ushort, "equipModelId", default=0,
        tooltip="Weapon model ID.",
    )
    WeaponIcon: Texture = ParamField(
        ushort, "iconId", default=0,
        tooltip="Weapon icon texture ID.",
    )
    InitialDurability: int = ParamField(
        ushort, "durability", default=100,
        tooltip="Durability of weapon when it is obtained. Always equal to max durability in vanilla game.",
    )
    MaxDurability: int = ParamField(
        ushort, "durabilityMax", default=100,
        tooltip="Maximum durability of weapon.",
    )
    ThrowEscapePower: int = ParamField(
        ushort, "attackThrowEscape", default=0, hide=True,
        tooltip="Power for escaping throws. Always 1, except for a few (and only a few) of the ghost replacement "
                "weapons.",
    )
    MaxParryWindowDuration: int = ParamField(
        short, "parryDamageLife", default=-1, hide=True,
        tooltip="Maximum parry window duration (cannot exceed TAE duration). Always set to 10.",
    )
    BasePhysicalDamage: int = ParamField(
        ushort, "attackBasePhysics", default=100,
        tooltip="Base physical damage of weapon attacks.",
    )
    BaseMagicDamage: int = ParamField(
        ushort, "attackBaseMagic", default=100,
        tooltip="Base magic damage of weapon attacks.",
    )
    BaseFireDamage: int = ParamField(
        ushort, "attackBaseFire", default=100,
        tooltip="Base fire damage of weapon attacks.",
    )
    BaseLightningDamage: int = ParamField(
        ushort, "attackBaseThunder", default=100,
        tooltip="Base lightning damage of weapon attacks.",
    )
    BaseStaminaDamage: int = ParamField(
        ushort, "attackBaseStamina", default=100,
        tooltip="Base stamina damage of weapon attacks.",
    )
    BasePoiseDamage: int = ParamField(
        ushort, "saWeaponDamage", default=0,
        tooltip="Base poise damage of weapon attacks.",
    )
    AttackPoiseBonus: int = ParamField(
        short, "saDurability", default=0, hide=True,
        tooltip="Poise gained during attack animations with this weapon. Never used (probably done in TAE).",
    )
    EffectiveGuardAngle: int = ParamField(
        short, "guardAngle", default=0, hide=True,
        tooltip="Angle that can be guarded with this weapon. Never used.",
    )
    GuardStaminaDefense: int = ParamField(
        short, "staminaGuardDef", default=0,
        tooltip="Defense against (i.e. value subtracted from) stamina attack damage while guarding.",
    )
    WeaponUpgradeID: WeaponUpgradeParam = ParamField(
        short, "reinforceTypeId", default=0,
        tooltip="Weapon Upgrade parameter that specifies upgrade benefits.",
    )
    AllWeaponsAchievementGroup: int = ParamField(
        short, "compTrophySedId", default=-1, hide=True,
        tooltip="Index of weapon as it contributes to the Knight's Honor achievement.",
    )
    MaxUpgradeAchievementID: int = ParamField(
        short, "trophySeqId", default=-1, hide=True,
        tooltip="Achievement unlocked when weapon is upgraded to maximum level (one per upgrade path).",
    )
    ThrowDamageChangePercentage: int = ParamField(
        short, "throwAtkRate", default=0,
        tooltip="Percentage damage increase (if positive) or decrease (if negative) during backstabs and ripostes "
                "with this weapon.",
    )
    BowRangeChangePercentage: int = ParamField(
        short, "bowDistRate", default=0,
        tooltip="Percentage range increase (if positive) or decrease (if negative) with this bow.",
    )
    WeaponModelCategory: EQUIP_MODEL_CATEGORY = ParamField(
        byte, "equipModelCategory", default=7, hide=True,
        tooltip="Model category for equipment. Only one option for weapons.",
    )
    WeaponModelGender: EQUIP_MODEL_GENDER = ParamField(
        byte, "equipModelGender", default=0, hide=True,
        tooltip="Model gender variant. All weapons are genderless.",
    )
    WeaponCategory: WEAPON_CATEGORY = ParamField(
        byte, "weaponCategory", default=0,
        tooltip="Basic category of weapon. Many 'weapon types' you may be familiar with are merged here (e.g. whips "
                "are straight swords).",
    )
    AttackAnimationCategory: WEPMOTION_CATEGORY = ParamField(
        byte, "wepmotionCategory", default=0,
        tooltip="Basic weapon attack animation type. More diverse than WeaponCategory. This number is multiplied by "
                "10000 and used as an animation offset for all attacks, I believe.",
    )
    GuardAnimationCategory: GUARDMOTION_CATEGORY = ParamField(
        byte, "guardmotionCategory", default=0,
        tooltip="Basic weapon/shield block animation type.",
    )
    VisualSoundEffectsOnHit: WEP_MATERIAL_ATK = ParamField(
        byte, "atkMaterial", default=0,
        tooltip="Determines the sounds and visual effects generated when this weapon hits.",
    )
    VisualEffectsOnBlock: WEP_MATERIAL_DEF = ParamField(
        byte, "defMaterial", default=0,
        tooltip="Determines the visual effects generated when this weapon blocks an attack.",
    )
    SoundEffectsOnBlock: WEP_MATERIAL_DEF_SFX = ParamField(
        byte, "defSfxMaterial", default=0,
        tooltip="Determines the sound effects generated when this weapon blocks an attack.",
    )
    ScalingFormulaType: WEP_CORRECT_TYPE = ParamField(
        byte, "correctType", default=0,
        tooltip="Determines how scaling changes with attribute level.",
    )
    ElementAttribute: ATKPARAM_SPATTR_TYPE = ParamField(
        byte, "spAttribute", default=0,
        tooltip="Element attached to hits with this weapon.",
    )
    SpecialAttackCategory: WEPMOTION_CATEGORY = ParamField(
        byte, "spAtkcategory", default=0,
        tooltip="Overrides AttackAnimationCategory for some attacks. Ranges from 50 to 199 (or 0 for none). Often "
                "used to give weapons unique strong (R2) attacks, for example, but can override any attack animation.",
    )
    OneHandedAnimationCategory: WEPMOTION_CATEGORY = ParamField(
        byte, "wepmotionOneHandId", default=0,
        tooltip="Animation category for one-handed non-attack animations (like walking).",
    )
    TwoHandedAnimationCategory: WEPMOTION_CATEGORY = ParamField(
        byte, "wepmotionBothHandId", default=0,
        tooltip="Animation category for two-handed non-attack animations (like walking).",
    )
    RequiredStrength: int = ParamField(
        byte, "properStrength", default=0,
        tooltip="Required strength to wield weapon properly. (Reduced by one third if held two-handed.)",
    )
    RequiredDexterity: int = ParamField(
        byte, "properAgility", default=0,
        tooltip="Required dexterity to wield weapon properly.",
    )
    RequiredIntelligence: int = ParamField(
        byte, "properMagic", default=0,
        tooltip="Required intelligence to wield weapon properly.",
    )
    RequiredFaith: int = ParamField(
        byte, "properFaith", default=0,
        tooltip="Required faith to wield weapon properly.",
    )
    OverStrength: int = ParamField(
        byte, "overStrength", default=0, hide=True,
        tooltip="Unknown. Always set to 99, except for arrows and bolts.",
    )
    AttackBaseParry: int = ParamField(
        byte, "attackBaseParry", default=0, hide=True,
        tooltip="Unknown. Never used.",
    )
    DefenseBaseParry: int = ParamField(
        byte, "defenseBaseParry", default=0, hide=True,
        tooltip="Unknown. Never used.",
    )
    DeflectOnBlock: int = ParamField(
        byte, "guardBaseRepel", default=0,
        tooltip="Determines if an enemy will be deflected when you block them with this weapon (by comparing it to "
                "their DeflectOnAttack).",
    )
    DeflectOnAttack: int = ParamField(
        byte, "attackBaseRepel", default=0,
        tooltip="Determines if this weapon will be deflected when attacking a blocking enemy (by comparing it to "
                "their DeflectOnBlock).",
    )
    IgnoreGuardPercentage: int = ParamField(
        sbyte, "guardCutCancelRate", default=0, hide=True,
        tooltip="Percentage (from -100 to 100) of target's current guard rate to ignore. A value of 100 will ignore "
                "guarding completely, and a value of -100 will double their guarding effectiveness. Never used, in "
                "favor of the simple 'IgnoreGuard' boolean field.",
    )
    GuardLevel: int = ParamField(
        sbyte, "guardLevel", default=0,
        tooltip="Internal description: 'in which guard motion is the enemy attacked when guarded?' Exact effects are "
                "unclear, but this ranges from 0 to 4 in effectiveness of blocking in a predictable way (daggers are "
                "worse than swords, which are worse than greatswords, which are worse than all shields).",
    )
    SlashDamageReductionWhenGuarding: int = ParamField(
        sbyte, "slashGuardCutRate", default=0, hide=True,
        tooltip="Always zero.",
    )
    StrikeDamageReductionWhenGuarding: int = ParamField(
        sbyte, "blowGuardCutRate", default=0, hide=True,
        tooltip="Always zero.",
    )
    ThrustDamageReductionWhenGuarding: int = ParamField(
        sbyte, "thrustGuardCutRate", default=0, hide=True,
        tooltip="Always zero.",
    )
    PoisonDamageReductionWhenGuarding: int = ParamField(
        sbyte, "poisonGuardResist", default=0,
        tooltip="Percentage of incoming poison damage ignored when guarding.",
    )
    ToxicDamageReductionWhenGuarding: int = ParamField(
        sbyte, "diseaseGuardResist", default=0,
        tooltip="Percentage of incoming toxic damage ignored when guarding.",
    )
    BleedDamageReductionWhenGuarding: int = ParamField(
        sbyte, "bloodGuardResist", default=0,
        tooltip="Percentage of incoming bleed damage ignored when guarding.",
    )
    CurseDamageReductionWhenGuarding: int = ParamField(
        sbyte, "curseGuardResist", default=0,
        tooltip="Percentage of incoming curse damage ignored when guarding.",
    )
    DurabilityDivergenceCategory: DURABILITY_DIVERGENCE_CATEGORY = ParamField(
        byte, "isDurabilityDivergence", default=0,
        tooltip="Determines an alternate animation used if the player tries to use this weapon's special attack "
                "without having enough durability to use it. Exact enumeration is unknown, but existing usages are "
                "documented.",
    )
    RightHandAllowed: bool = ParamField(
        byte, "rightHandEquipable:1", bit_count=1, default=True,
        tooltip="If True, this weapon can be equipped in the right hand.",
    )
    LeftHandAllowed: bool = ParamField(
        byte, "leftHandEquipable:1", bit_count=1, default=True,
        tooltip="If True, this weapon can be equipped in the left hand.",
    )
    BothHandsAllowed: bool = ParamField(
        byte, "bothHandEquipable:1", bit_count=1, default=True,
        tooltip="If True, this weapon can be held in two-handed mode.",
    )
    UsesEquippedArrows: bool = ParamField(
        byte, "arrowSlotEquipable:1", bit_count=1, default=False,
        tooltip="If True, this weapon will use equipped arrow slot.",
    )
    UsesEquippedBolts: bool = ParamField(
        byte, "boltSlotEquipable:1", bit_count=1, default=False,
        tooltip="If True, this weapon will use equipped bolt slot.",
    )
    GuardEnabled: bool = ParamField(
        byte, "enableGuard:1", bit_count=1, default=False,
        tooltip="If True, the player can guard with this weapon by holding L1.",
    )
    ParryEnabled: bool = ParamField(
        byte, "enableParry:1", bit_count=1, default=False,
        tooltip="If True, the player can parry with this weapon by pressing L2.",
    )
    CanCastSorceries: bool = ParamField(
        byte, "enableMagic:1", bit_count=1, default=False,
        tooltip="If True, this weapon can be used to cast sorceries.",
    )
    CanCastPyromancy: bool = ParamField(
        byte, "enableSorcery:1", bit_count=1, default=False,
        tooltip="If True, this weapon can be used to cast pyromancy.",
    )
    CanCastMiracles: bool = ParamField(
        byte, "enableMiracle:1", bit_count=1, default=False,
        tooltip="If True, this weapon can be used to cast miracles.",
    )
    CanCastCovenantMagic: bool = ParamField(
        byte, "enableVowMagic:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    DealsNeutralDamage: bool = ParamField(
        byte, "isNormalAttackType:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    DealsStrikeDamage: bool = ParamField(
        byte, "isBlowAttackType:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    DealsSlashDamage: bool = ParamField(
        byte, "isSlashAttackType:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    DealsThrustDamage: bool = ParamField(
        byte, "isThrustAttackType:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    IsUpgraded: bool = ParamField(
        byte, "isEnhance:1", bit_count=1, default=True,
        tooltip="TODO",
    )
    IsAffectedByLuck: bool = ParamField(
        byte, "isLuckCorrect:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    IsCustom: bool = ParamField(
        byte, "isCustom:1", bit_count=1, default=True,
        tooltip="TODO",
    )
    DisableBaseChangeReset: bool = ParamField(
        byte, "disableBaseChangeReset:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    DisableRepairs: bool = ParamField(
        byte, "disableRepair:1", bit_count=1, default=False,
        tooltip="If True, this weapon cannot be repaired.",
    )
    IsDarkHand: bool = ParamField(
        byte, "isDarkHand:1", bit_count=1, default=False, hide=True,
        tooltip="Enabled only for the Dark Hand.",
    )
    SimpleDLCModelExists: bool = ParamField(
        byte, "simpleModelForDlc:1", bit_count=1, default=False, hide=True,
        tooltip="Unknown; always set to False.",
    )
    IsLantern: bool = ParamField(
        byte, "lanternWep:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    CanHitGhosts: bool = ParamField(
        byte, "isVersusGhostWep:1", bit_count=1, default=False,
        tooltip="If True, this weapon can hit ghosts without a Transient Curse active.",
    )
    BaseChangeCategory: int = ParamField(
        byte, "baseChangeCategory:6", bit_count=6, default=0, hide=True,
        tooltip="Never used. Likely Demon's Souls junk.",
    )
    IsDragonSlayer: bool = ParamField(
        byte, "isDragonSlayer:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    CanBeStored: bool = ParamField(
        byte, "isDeposit:1", bit_count=1, default=True,
        tooltip="If True, this weapon can be stored in the Bottomless Box. Always True for rings.",
    )
    DisableMultiplayerShare: bool = ParamField(
        byte, "disableMultiDropShare:1", bit_count=1, default=False, hide=True,
        tooltip="If True, this weapon cannot be given to other players by dropping it. Always False in vanilla.",
    )
    InvisibleInCutscenes: EQUIP_BOOL = ParamField(
        byte, "invisibleOnRemo:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    IsAttributeWeapon: EQUIP_BOOL = ParamField(
        byte, "isAttributeWep:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    EnchantsLeftHand: EQUIP_BOOL = ParamField(
        byte, "isEnchantLeftHand:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    CanDropToSummons: EQUIP_BOOL = ParamField(
        byte, "isGuestDrop:1", bit_count=1, default=False,
        tooltip="TODO",
    )
    BeastResistanceOnGuard: int = ParamField(
        sbyte, "therianthropeGuardResist", default=0,
        tooltip="TODO",
    )
    PhysicalAttackMenuDisplayType: PHYS_ATK_MENU_DISP_TYPE = ParamField(
        byte, "PhysAtkMenuDispType", default=0,
        tooltip="TODO",
    )
    WeaponMotionHangType: int = ParamField(
        byte, "wepmotionHangType", default=0,
        tooltip="TODO",
    )
    Slot0RightHangModelPoint: int = ParamField(
        short, "dmypolyId_Slot0RightHang", default=-1,
        tooltip="TODO",
    )
    Slot0RightFormAModelPoint: int = ParamField(
        short, "dmypolyId_Slot0RightFormA", default=-1,
        tooltip="TODO",
    )
    Slot0RightFormBModelPoint: int = ParamField(
        short, "dmypolyId_Slot0RightFormB", default=-1,
        tooltip="TODO",
    )
    Slot0LeftHangModelPoint: int = ParamField(
        short, "dmypolyId_Slot0LeftHang", default=-1,
        tooltip="TODO",
    )
    Slot0LeftFormAModelPoint: int = ParamField(
        short, "dmypolyId_Slot0LeftFormA", default=-1,
        tooltip="TODO",
    )
    Slot0LeftFormBModelPoint: int = ParamField(
        short, "dmypolyId_Slot0LeftFormB", default=-1,
        tooltip="TODO",
    )
    Slot1RightHangModelPoint: int = ParamField(
        short, "dmypolyId_Slot1RightHang", default=-1,
        tooltip="TODO",
    )
    Slot1RightFormAModelPoint: int = ParamField(
        short, "dmypolyId_Slot1RightFormA", default=-1,
        tooltip="TODO",
    )
    Slot1RightFormBModelPoint: int = ParamField(
        short, "dmypolyId_Slot1RightFormB", default=-1,
        tooltip="TODO",
    )
    Slot1LeftHangModelPoint: int = ParamField(
        short, "dmypolyId_Slot1LeftHang", default=-1,
        tooltip="TODO",
    )
    Slot1LeftFormAModelPoint: int = ParamField(
        short, "dmypolyId_Slot1LeftFormA", default=-1,
        tooltip="TODO",
    )
    Slot1LeftFormBModelPoint: int = ParamField(
        short, "dmypolyId_Slot1LeftFormB", default=-1,
        tooltip="TODO",
    )
    Slot2RightHangModelPoint: int = ParamField(
        short, "dmypolyId_Slot2RightHang", default=-1,
        tooltip="TODO",
    )
    Slot2RightFormAModelPoint: int = ParamField(
        short, "dmypolyId_Slot2RightFormA", default=-1,
        tooltip="TODO",
    )
    Slot2RightFormBModelPoint: int = ParamField(
        short, "dmypolyId_Slot2RightFormB", default=-1,
        tooltip="TODO",
    )
    Slot2LeftHangModelPoint: int = ParamField(
        short, "dmypolyId_Slot2LeftHang", default=-1,
        tooltip="TODO",
    )
    Slot2LeftFormAModelPoint: int = ParamField(
        short, "dmypolyId_Slot2LeftFormA", default=-1,
        tooltip="TODO",
    )
    Slot2LeftFormBModelPoint: int = ParamField(
        short, "dmypolyId_Slot2LeftFormB", default=-1,
        tooltip="TODO",
    )
    Slot3RightHangModelPoint: int = ParamField(
        short, "dmypolyId_Slot3RightHang", default=-1,
        tooltip="TODO",
    )
    Slot3RightFormAModelPoint: int = ParamField(
        short, "dmypolyId_Slot3RightFormA", default=-1,
        tooltip="TODO",
    )
    Slot3RightFormBModelPoint: int = ParamField(
        short, "dmypolyId_Slot3RightFormB", default=-1,
        tooltip="TODO",
    )
    Slot3LeftHangModelPoint: int = ParamField(
        short, "dmypolyId_Slot3LeftHang", default=-1,
        tooltip="TODO",
    )
    Slot3LeftFormAModelPoint: int = ParamField(
        short, "dmypolyId_Slot3LeftFormA", default=-1,
        tooltip="TODO",
    )
    Slot3LeftFormBModelPoint: int = ParamField(
        short, "dmypolyId_Slot3LeftFormB", default=-1,
        tooltip="TODO",
    )
    WeaponRegainHP: int = ParamField(
        ushort, "wepRegainHp", default=0,
        tooltip="TODO",
    )
    BulletCost: int = ParamField(
        sbyte, "bulletConsumeNum", default=-1,
        tooltip="TODO",
    )
    StorageCategory: int = ParamField(
        byte, "repositoryCategory", default=0,
        tooltip="TODO",
    )

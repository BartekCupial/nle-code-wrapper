from __future__ import annotations

import enum
import re

from nle import nethack as nh

from nle_code_wrapper.bot.character.skill import Skill


class ItemClass(enum.Enum):
    RANDOM = nh.RANDOM_CLASS  # used for generating random objects
    ILLOBJ = nh.ILLOBJ_CLASS
    COIN = nh.COIN_CLASS
    AMULET = nh.AMULET_CLASS
    WEAPON = nh.WEAPON_CLASS
    ARMOR = nh.ARMOR_CLASS
    COMESTIBLES = nh.FOOD_CLASS
    SCROLL = nh.SCROLL_CLASS
    SPELLBOOK = nh.SPBOOK_CLASS
    POTION = nh.POTION_CLASS
    RING = nh.RING_CLASS
    WAND = nh.WAND_CLASS
    TOOL = nh.TOOL_CLASS
    GEM = nh.GEM_CLASS
    ROCK = nh.ROCK_CLASS
    BALL = nh.BALL_CLASS
    CHAIN = nh.CHAIN_CLASS
    VENOM = nh.VENOM_CLASS
    CORPSE = nh.MAXOCLASSES
    STATUE = nh.MAXOCLASSES + 1
    MONSTER = nh.MAXOCLASSES + 2

    @classmethod
    def from_oclass(cls, oclass: int) -> ItemClass:
        return cls(oclass)

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class WeaponClass(enum.Enum):
    WEAPON = 0
    BOW = 1
    PROJECTILE = 2

    @classmethod
    def from_oc_skill(cls, oc_skill: int):
        if oc_skill < 0:
            return WeaponClass.PROJECTILE
        elif Skill(oc_skill) in [Skill.BOW, Skill.CROSSBOW, Skill.SLING]:
            return WeaponClass.BOW
        else:
            return WeaponClass.WEAPON

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class ArmorClass(enum.Enum):
    SUIT = 0
    SHIELD = 1
    HELM = 2
    GLOVES = 3
    BOOTS = 4
    CLOAK = 5
    SHIRT = 6

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class ToolClass(enum.Enum):
    TOOL = 0
    WEPTOOL = 1  # tools useful as weapons
    CONTAINER = 2  # containers
    KEY = 3

    @classmethod
    def from_obj(cls, obj):
        return cls()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class GemClass(enum.Enum):
    GEM = 0
    ROCK = 1

    @classmethod
    def from_name(cls, name):
        if name in [
            "luckstone",
            "loadstone",
            "touchstone",
            "rock",
            "flint stone",
            "gray stone",
        ]:
            return GemClass.ROCK
        else:
            return GemClass.GEM

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class ItemQuantity:
    def __init__(self, value: int, repr: str):
        self.value = value
        self.repr = repr

    def __eq__(self, other) -> bool:
        if isinstance(other, ItemQuantity):
            return self.value == other.value
        return False

    @classmethod
    def from_str(cls, str: str):
        return cls(int({"a": 1, "an": 1, "the": 1}.get(str, str)), str)

    def __str__(self):
        return self.repr

    def __repr__(self):
        return str(self)


class ItemBeatitude(enum.Enum):
    # beatitude
    UNKNOWN = 0
    CURSED = 1
    UNCURSED = 2
    BLESSED = 3

    @classmethod
    def from_str(cls, str: str) -> ItemBeatitude:
        return cls({"": 0, "cursed": 1, "uncursed": 2, "blessed": 3}[str])

    def __str__(self):
        match self:
            case ItemBeatitude.UNKNOWN:
                return ""
            case _:
                return self.name.lower()

    def __repr__(self):
        return str(self)


class ItemEnchantment:
    def __init__(self, value: int = None, unknown: bool = False):
        self.value = value
        self.unknown = unknown

    def __eq__(self, other: ItemEnchantment) -> bool:
        if isinstance(other, ItemEnchantment):
            return self.value == other.value and self.unknown == other.unknown
        return False

    @classmethod
    def from_str(cls, str: str):
        if str == "":
            return cls(0, unknown=True)
        else:
            return cls({"+": 1, "-": -1}[str[0]] * int(str[1:]))

    def __str__(self):
        return "" if self.unknown else f"{'+' if self.value >= 0 else '-'}{self.value}"

    def __repr__(self):
        return str(self)


class ItemErosion(enum.Enum):
    NONE = 0  # No erosion
    BASIC = 1  # Basic damage (no prefix)
    HEAVY = 2  # Heavy damage (prefix: 'very')
    SEVERE = 3  # Severe damage (prefix: 'thoroughly')

    @classmethod
    def from_str(cls, str: str) -> ItemErosion:
        # rusty, very rusty, thoroughly rusty
        # corroded, very corroded, thoroughly corroded
        # burnt, very burnt, thoroughly burnt
        # rotten, very rotten, thoroughly rotten
        damage_pattern = re.compile(r"(?:(very|thoroughly)\s+)?(rusty|burnt|corroded|rotted)(?:\s+|$)")

        # Find all matches in the text
        matches = damage_pattern.finditer(str)

        intensity_map = {None: 1, "very": 2, "thoroughly": 3}  # Basic damage  # Heavy damage  # Severe damage

        damages = []
        for match in matches:
            intensity_word, damage_type = match.groups()
            damages.append(intensity_map[intensity_word])
        erosion = max(damages) if damages else 0
        return cls(erosion)

    def __str__(self):
        match self:
            case ItemErosion.NONE:
                return ""
            case ItemErosion.BASIC:
                return "eroded"
            case ItemErosion.HEAVY:
                return "very eroded"
            case ItemErosion.SEVERE:
                return "thoroughly eroded"

    def __repr__(self):
        return str(self)


class ShopStatus(enum.Enum):
    NOT_SHOP = 0
    FOR_SALE = 1
    UNPAID = 2

    @classmethod
    def from_str(cls, str: str) -> ShopStatus:
        return cls({"": 0, "for sale": 1, "unpaid": 2}[str])

    def __str__(self):
        match self:
            case ShopStatus.NOT_SHOP:
                return ""
            case ShopStatus.FOR_SALE:
                return "for sale"
            case ShopStatus.UNPAID:
                return "unpaid"

    def __repr__(self):
        return str(self)


class ShopPrice:
    def __init__(self, value: int):
        self.value = value

    @classmethod
    def from_str(cls, str: str):
        if str == "":
            return cls(0)
        else:
            return cls(int(str))

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

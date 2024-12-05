from __future__ import annotations

from typing import Dict, List

import numpy as np
from nle import nethack
from nle_utils.item import ItemBeatitude, ItemClasses, ItemEnchantment, ItemErosion, ItemShopStatus

OBJECT_NAMES = {
    (nethack.OBJ_NAME(nethack.objclass(index)), nethack.objclass(index).oc_class): nethack.objclass(index)
    for index in range(nethack.NUM_OBJECTS)
}
OBJECT_DESCRS = {
    (nethack.OBJ_DESCR(nethack.objclass(index)), nethack.objclass(index).oc_class): nethack.objclass(index)
    for index in range(nethack.NUM_OBJECTS)
}


def get_object(full_name, obj_class):
    candidates = []
    for (obj_name, oc_class), obj in OBJECT_NAMES.items():
        if obj_name is None:
            continue

        if obj_name in full_name and chr(obj_class.value) == oc_class:
            candidates.append((obj_name, obj))

    for (obj_descr, oc_class), obj in OBJECT_DESCRS.items():
        if obj_descr is None:
            continue

        if obj_descr in full_name and chr(obj_class.value) == oc_class:
            candidates.append((obj_descr, obj))

    if len(candidates) > 1:
        # take longest match, example "dark green" will match with green and dark green, take dark green
        candidates = [sorted(candidates, key=lambda x: len(x[0]), reverse=True)[0]]

    assert len(candidates) == 1, f"Multiple candidates found: {candidates}"
    return candidates[0][1]


def get_object_name(obj):
    return nethack.objdescr.from_idx(obj.oc_name_idx).oc_name


def get_object_weight(obj):
    """
    Calculate the weight of the given object, including recursive calculation
    of contained objects' weights.

    Args:
        obj: The object to calculate weight for

    Returns:
        int: Total weight of the object
    """
    # TODO: recursive calculation
    return obj.oc_weight


def arm_bonus(obj, enchantment: int, erosion: int):
    return obj.a_ac + enchantment - min(erosion, obj.a_ac)


class Item:
    def __init__(
        self,
        letter: int,
        name: np.ndarray,
        oclass: int,
        glyph: int,
        shop_status: int = None,
    ):
        self.letter = letter
        self.glyph = glyph
        self.full_name = "".join(map(chr, name)).rstrip("\x00")
        self.item_class = ItemClasses.from_oclass(oclass)
        self.beatitude = ItemBeatitude.from_name(self.full_name)
        self.enchantment = ItemEnchantment.from_name(self.full_name)
        self.erosion = ItemErosion.from_name(self.full_name)

        self.shop_status = ItemShopStatus(shop_status) if shop_status is not None else None

        self.object = get_object(self.full_name, self.item_class)
        self.name = get_object_name(self.object)
        self.weight = get_object_weight(self.object)

    @property
    def in_use(self):
        if "(" in self.full_name:
            return True
        else:
            return False

    @property
    def quantity(self):
        if self.full_name.split(" ")[0].isdigit():
            return int(self.full_name.split(" ")[0])
        else:
            return 1

    """
    WEAPON
    """

    @property
    def is_weapon(self):
        return self.item_class == ItemClasses.WEAPONS

    @property
    def is_launcher(self):
        if not self.is_weapon:
            return False

        return self.name in ["bow", "long bow", "elven bow", "orcish bow", "yumi", "crossbow", "sling"]

    @property
    def is_firing_projectile(self, launcher: Item = None):
        if not self.is_weapon:
            return False

        arrows = ["arrow", "elven arrow", "orcish arrow", "silver arrow", "ya"]

        if launcher is None:
            return arrows + ["crossbow bolt"]  # TODO: sling ammo

        if launcher.name == "crossbow":
            return self.name == "crossbow bolt"

        if launcher.name == "sling":
            # TODO: implement sling ammo validation
            return False

        bows = ["bow", "long bow", "elven bow", "orcish bow", "yumi"]
        if launcher.name in bows:
            return self.name in arrows

        raise ValueError(f"Unknown launcher type: {launcher.name}")

    @property
    def is_thrown_projectile(self):
        if not self.is_weapon:
            return False

        return self.name in [
            "boomerang",
            "dagger",
            "elven dagger",
            "orcish dagger",
            "silver dagger",
            "worm tooth",
            "crysknife",
            "knife",
            "athame",
            "scalpel",
            "stiletto",
            "dart",
            "shuriken",
        ]

    """
    ARMOR
    """

    @property
    def is_armor(self):
        return self.item_class == ItemClasses.ARMOR

    @property
    def arm_bonus(self):
        return arm_bonus(self.object, self.enchantment.value, self.erosion.value)

    def __str__(self):
        return f"{chr(self.letter)}) {self.full_name}"


class Inventory:
    def __init__(self, inv_strs, inv_letters, inv_oclasses, inv_glyphs):
        self.items = []
        for i in range(len(inv_strs)):
            letter = inv_letters[i]
            name = inv_strs[i]
            oclass = inv_oclasses[i]
            glyph = inv_glyphs[i]

            if letter == 0:
                break

            item = Item(letter, name, oclass, glyph)
            self.items.append(item)

        self.inventory: Dict[str, List[Item]] = {}
        inventory_classes = {
            "coins": [ItemClasses.COINS],
            "amulets": [ItemClasses.AMULETS],
            "weapons": [ItemClasses.WEAPONS],
            "armor": [ItemClasses.ARMOR],
            "compestibles": [ItemClasses.COMPESTIBLES],
            "scrolls": [ItemClasses.SCROLLS],
            "spellbooks": [ItemClasses.SPELLBOOKS],
            "potions": [ItemClasses.POTIONS],
            "rings": [ItemClasses.RINGS],
            "wands": [ItemClasses.WANDS],
            "tools": [
                ItemClasses.TOOLS,
                ItemClasses.GEMS,
                ItemClasses.ROCKS,
                ItemClasses.BALL,
                ItemClasses.CHAIN,
                ItemClasses.VENOM,
            ],
        }
        for key, classes in inventory_classes.items():
            self.inventory[key] = [item for item in self.items if item.item_class in classes]

    def __getitem__(self, key) -> List[Item]:
        return self.inventory[key]

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __str__(self):
        return "Inventory:\n\t" + "\n\t".join(
            f"{key}:\n\t\t" + "\n\t\t".join(str(item) for item in category)
            for key, category in self.inventory.items()
            if category
        )


if __name__ == "__main__":
    import gym
    import nle

    env = gym.make("NetHackScore-v0")
    obs = env.reset()

    inv_glyphs = obs["inv_glyphs"]
    inv_letters = obs["inv_letters"]
    inv_oclasses = obs["inv_oclasses"]
    inv_strs = obs["inv_strs"]

    inventory = Inventory(inv_strs, inv_letters, inv_oclasses, inv_glyphs)
    print(inventory)

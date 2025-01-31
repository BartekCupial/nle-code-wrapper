from __future__ import annotations

import enum
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from nle import nethack as nh
from nle_utils.item import ArmorType, ItemBeatitude, ItemClasses, ItemEnchantment, ItemErosion, ItemShopStatus


class GlyphCategory(enum.Enum):
    OTHER = -1
    ITEM = 0
    MONSTER = 1
    CORPSE = 2
    STATUE = 3


def name_and_category_from_glyph(glyph) -> Tuple[str, GlyphCategory]:
    name = ""
    category = GlyphCategory.OTHER

    if glyph >= nh.GLYPH_STATUE_OFF:
        permonst = nh.permonst(nh.glyph_to_mon(glyph))
        mon_name = permonst.mname
        name = mon_name + " statue"

        obj = nh.objclass(nh.glyph_to_obj(glyph))
        category = GlyphCategory.STATUE
    elif glyph >= nh.GLYPH_WARNING_OFF:
        pass
    elif glyph >= nh.GLYPH_SWALLOW_OFF:
        pass
    elif glyph >= nh.GLYPH_ZAP_OFF:
        pass
    elif glyph >= nh.GLYPH_EXPLODE_OFF:
        pass
    elif glyph >= nh.GLYPH_CMAP_OFF:
        pass
    elif glyph >= nh.GLYPH_OBJ_OFF:
        obj_name = ""
        obj_description = ""

        obj = nh.objclass(nh.glyph_to_obj(glyph))
        obj_class = obj.oc_class
        category = GlyphCategory.ITEM

        if nh.OBJ_NAME(obj) is not None:
            obj_name = nh.OBJ_NAME(obj)
        if nh.OBJ_DESCR(obj) is not None:
            obj_description = nh.OBJ_DESCR(obj)

        match ItemClasses(ord(obj_class)):
            case ItemClasses.ILLOBJ:
                name = obj_name
            case ItemClasses.WEAPON:
                name = obj_name
            case ItemClasses.ARMOR:
                if len(obj_name) > 0:
                    name = obj_name
                else:
                    name = obj_description
            case ItemClasses.RING:
                name = obj_name if "ring" in obj_name else "ring of " + obj_name
            case ItemClasses.AMULET:
                name = obj_name
            case ItemClasses.TOOL:
                name = obj_name
            case ItemClasses.COMESTIBLES:
                name = obj_name + obj_description
            case ItemClasses.POTION:
                name = obj_name if "potion" in obj_name else "potion of " + obj_name
            case ItemClasses.SCROLL:
                name = obj_name if "scroll" in obj_name else "scroll of " + obj_name
            case ItemClasses.SPELLBOOK:
                name = obj_name if "spellbook" in obj_name else "spellbook of " + obj_name
            case ItemClasses.WAND:
                name = obj_name if "wand" in obj_name else "wand of " + obj_name
            case ItemClasses.COIN:
                name = obj_name
            case ItemClasses.GEM:
                name = obj_name
            case ItemClasses.ROCK:
                name = obj_name
            case ItemClasses.BALL:
                name = obj_name
            case ItemClasses.CHAIN:
                name = obj_name
            case ItemClasses.VENOM:
                name = "splash of " + obj_name
            case _:
                name = ""
    elif glyph >= nh.GLYPH_RIDDEN_OFF:
        permonst = nh.permonst(nh.glyph_to_mon(glyph))
        mon_name = permonst.mname
        name = "ridden " + mon_name
        category = GlyphCategory.MONSTER
    elif glyph >= nh.GLYPH_BODY_OFF:
        monster_idx = glyph - nh.GLYPH_BODY_OFF
        permonst = nh.permonst(monster_idx)
        name = permonst.mname + " corpse"
        category = GlyphCategory.CORPSE
    elif glyph >= nh.GLYPH_DETECT_OFF:
        permonst = nh.permonst(nh.glyph_to_mon(glyph))
        mon_name = permonst.mname
        name = "detected " + mon_name
    elif glyph >= nh.GLYPH_INVIS_OFF:
        name = "invisible creature"
    elif glyph >= nh.GLYPH_PET_OFF:
        permonst = nh.permonst(nh.glyph_to_mon(glyph))
        mon_name = permonst.mname
        name = "tame " + mon_name
        category = GlyphCategory.MONSTER
    else:
        permonst = nh.permonst(nh.glyph_to_mon(glyph))
        mon_name = permonst.mname
        name = mon_name
        category = GlyphCategory.MONSTER

    return name, category


@dataclass
class GlyphObject:
    glyph: int
    name: str
    category: GlyphCategory


GLYPH_TO_OBJECT: Dict[int, GlyphObject] = {}
for glyph in range(nh.MAX_GLYPH):
    name, category = name_and_category_from_glyph(glyph)
    GLYPH_TO_OBJECT[glyph] = GlyphObject(glyph, name, category)


class Item:
    def __init__(self, inv_letter, inv_str, inv_oclass, inv_glyph):
        glyph_object = GLYPH_TO_OBJECT[inv_glyph]

        self.glyph = inv_glyph
        self.name = glyph_object.name
        self.category = glyph_object.category
        self.letter = inv_letter
        self.full_name = bytes(inv_str).decode("latin-1")

        self.item_class = ItemClasses.from_oclass(inv_oclass)
        self.beatitude = ItemBeatitude.from_name(self.full_name)
        self.enchantment = ItemEnchantment.from_name(self.full_name)
        self.erosion = ItemErosion.from_name(self.full_name)
        # self.shop_status TODO:

    def __str__(self):
        return f"{chr(self.letter)}) {self.full_name}"

    def __repr__(self):
        return f"{chr(self.letter)}) {self.full_name}"

    @property
    def object(self):
        if self.category in [GlyphCategory.CORPSE, GlyphCategory.ITEM, GlyphCategory.STATUE]:
            return nh.objclass(nh.glyph_to_obj(self.glyph))
        else:
            return None

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
        return self.item_class == ItemClasses.WEAPON

    @property
    def main_hand(self):
        return (
            "(weapon in hands)" in self.full_name
            or "(weapon in right hand)" in self.full_name
            or "(weapon in left hand)" in self.full_name
            or "(wielded)" in self.full_name
        )

    @property
    def off_hand(self):
        return "(alternate weapon; not wielded)" in self.full_name

    @property
    def is_launcher(self):
        if not self.is_weapon:
            return False

        return self.name in ["bow", "long bow", "elven bow", "orcish bow", "yumi", "crossbow", "sling"]

    def can_shoot_projectile(self, projectile: Item):
        if not self.is_weapon:
            return False

        arrows = ["arrow", "elven arrow", "orcish arrow", "silver arrow", "ya"]

        if self.name == "crossbow":
            return projectile.name == "crossbow bolt"

        if self.name == "sling":
            # TODO: implement sling ammo validation
            return False

        bows = ["bow", "long bow", "elven bow", "orcish bow", "yumi"]
        if self.name in bows:
            return projectile.name in arrows

    @property
    def is_firing_projectile(self):
        if not self.is_weapon:
            return False

        return self.name in [
            "arrow",
            "elven arrow",
            "orcish arrow",
            "silver arrow",
            "ya",
            "crossbow bolt",
        ]  # TODO: sling ammo

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

    def arm_bonus(self):
        if self.object is None:
            return 0
        return self.object.a_ac + self.enchantment.value - min(self.erosion.value, self.object.a_ac)

    @property
    def is_worn(self):
        return "(being worn)" in self.full_name

    """
    COMESTIBLES
    """

    @property
    def is_corpse(self):
        return self.item_class == ItemClasses.COMESTIBLES and self.category == GlyphCategory.CORPSE

    @property
    def is_food(self):
        return self.item_class == ItemClasses.COMESTIBLES and self.category == GlyphCategory.ITEM

    """
    TOOLS
    """

    @property
    def is_key(self):
        return self.item_class == ItemClasses.TOOL and self.name in ["skeleton key", "lock pick", "credit card"]

    @property
    def nutrition(self):
        """Calculate base nutrition of a food object."""

        # Determine base nutrition value based on object type
        # NOTE: skipped globby and special cases for certain food types
        if self.category == GlyphCategory.CORPSE:
            monster_idx = self.glyph - nh.GLYPH_BODY_OFF
            permonst = nh.permonst(nh.glyph_to_mon(monster_idx))
            nut = permonst.cnutrit
        else:
            nut = self.object.oc_nutrition

        return nut

    @property
    def weight(self):
        if self.object is None:
            return 0

        wt = self.object.oc_weight

        # NOTE: we ignore globby, partly_eaten (food, corpses), candelabrum

        # container or statue
        # if (Is_container(obj) || obj->otyp == STATUE) {
        #     struct obj *contents;
        #     register int cwt = 0;

        #     if (obj->otyp == STATUE && obj->corpsenm >= LOW_PM)
        #         wt = (int) obj->quan * ((int) mons[obj->corpsenm].cwt * 3 / 2);

        #     for (contents = obj->cobj; contents; contents = contents->nobj)
        #         cwt += weight(contents);
        #     /*
        #      *  The weight of bags of holding is calculated as the weight
        #      *  of the bag plus the weight of the bag's contents modified
        #      *  as follows:
        #      *
        #      *      Bag status      Weight of contents
        #      *      ----------      ------------------
        #      *      cursed                  2x
        #      *      blessed                 x/4 [rounded up: (x+3)/4]
        #      *      otherwise               x/2 [rounded up: (x+1)/2]
        #      *
        #      *  The macro DELTA_CWT in pickup.c also implements these
        #      *  weight equations.
        #      */
        #     if (obj->otyp == BAG_OF_HOLDING)
        #         cwt = obj->cursed ? (cwt * 2) : obj->blessed ? ((cwt + 3) / 4)
        #                                                      : ((cwt + 1) / 2);

        #     return wt + cwt;
        # }
        # TODO:

        # corpse
        # if (obj->otyp == CORPSE && obj->corpsenm >= LOW_PM) {
        #     long long_wt = obj->quan * (long) mons[obj->corpsenm].cwt;

        #     wt = (long_wt > LARGEST_INT) ? LARGEST_INT : (int) long_wt;
        #     if (obj->oeaten)
        #         wt = eaten_stat(wt, obj);
        #     return wt;
        # long_wt = obj.quan * mons[obj.corpsenm].cwt
        if self.category == GlyphCategory.CORPSE:
            monster_idx = self.glyph - nh.GLYPH_BODY_OFF
            permonst = nh.permonst(nh.glyph_to_mon(monster_idx))
            return self.quantity * permonst.cwt
            # NOTE: we ignore partly eaten

        # coin
        # } else if (obj->oclass == COIN_CLASS) {
        #     return (int) ((obj->quan + 50L) / 100L);
        if self.item_class == ItemClasses.COIN:
            return (self.quantity + 50) // 100

        # heavy iron ball
        # } else if (obj->otyp == HEAVY_IRON_BALL && obj->owt != 0) {
        #     return (int) obj->owt; /* kludge for "very" heavy iron ball */
        # TODO:

        if wt:
            return wt * self.quantity
        else:
            return (self.quantity + 1) >> 1


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
            "coins": [ItemClasses.COIN],
            "amulets": [ItemClasses.AMULET],
            "weapons": [ItemClasses.WEAPON],
            "armor": [ItemClasses.ARMOR],
            "comestibles": [ItemClasses.COMESTIBLES],
            "scrolls": [ItemClasses.SCROLL],
            "spellbooks": [ItemClasses.SPELLBOOK],
            "potions": [ItemClasses.POTION],
            "rings": [ItemClasses.RING],
            "wands": [ItemClasses.WAND],
            "tools": [
                ItemClasses.TOOL,
                ItemClasses.GEM,
                ItemClasses.ROCK,
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

    @property
    def main_hand(self):
        wielded_weapon = [weapon for weapon in self["weapons"] if weapon.main_hand]
        return wielded_weapon[0] if wielded_weapon else None

    @property
    def off_hand(self):
        wielded_weapon = [weapon for weapon in self["weapons"] if weapon.off_hand]
        return wielded_weapon[0] if wielded_weapon else None

    @property
    def worn_armor_by_type(self):
        """Returns a dictionary of worn armor items indexed by their ArmorType."""
        worn_armor = [armor for armor in self["armor"] if armor.is_worn]
        return {
            armor_type: next((armor for armor in worn_armor if armor.object.oc_armcat == armor_type.value), None)
            for armor_type in ArmorType
        }

    @property
    def suit(self):
        return self.worn_armor_by_type[ArmorType.SUIT]

    @property
    def shield(self):
        return self.worn_armor_by_type[ArmorType.SHIELD]

    @property
    def helm(self):
        return self.worn_armor_by_type[ArmorType.HELM]

    @property
    def gloves(self):
        return self.worn_armor_by_type[ArmorType.GLOVES]

    @property
    def boots(self):
        return self.worn_armor_by_type[ArmorType.BOOTS]

    @property
    def cloak(self):
        return self.worn_armor_by_type[ArmorType.CLOAK]

    @property
    def shirt(self):
        return self.worn_armor_by_type[ArmorType.SHIRT]


if __name__ == "__main__":
    import gym
    import nle

    env = gym.make("NetHackScore-v0", character="@")
    for i in range(10):
        env.seed(i)
        obs = env.reset()

        inv_glyphs = obs["inv_glyphs"]
        inv_letters = obs["inv_letters"]
        inv_oclasses = obs["inv_oclasses"]
        inv_strs = obs["inv_strs"]

        inventory = Inventory(inv_strs, inv_letters, inv_oclasses, inv_glyphs)
        print(inventory)

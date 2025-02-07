from __future__ import annotations

import re
from typing import List, Optional

import inflect
from nle import nethack as nh

from nle_code_wrapper.bot.inventory.objects import NAME_TO_OBJECTS, name_to_monsters
from nle_code_wrapper.bot.inventory.properties import (
    ArmorClass,
    GemClass,
    ItemBeatitude,
    ItemClass,
    ItemEnchantment,
    ItemErosion,
    ItemQuantity,
    ShopPrice,
    ShopStatus,
    ToolClass,
    WeaponClass,
)

p = inflect.engine()


class Item:
    def __init__(
        self,
        text: str,
        letter: Optional[int],
        name: str,
        objects: List,
        permonst,
        quantity: ItemQuantity,
        beatitude: ItemBeatitude,
        erosion: ItemErosion,
        enchantment: ItemEnchantment,
        shop_status: ShopStatus,
        shop_price: ShopPrice,
        item_class: ItemClass,
        equipped: bool,
        at_ready: bool,
    ):
        self.text = text
        self.letter = letter

        self.name = name
        self.objects = objects
        self.permonst = permonst

        self.quantity = quantity
        self.beatitude = beatitude
        self.erosion = erosion
        self.enchantment = enchantment
        self.shop_status = shop_status
        self.shop_price = shop_price
        self.item_class = item_class

        self.equipped = equipped
        self.at_ready = at_ready

        self.tool_class

    @classmethod
    def from_text(cls, text: str, letter: Optional[int] = None):
        properties = cls.parse_item_text(text)
        return cls(
            text=text,
            letter=letter,
            name=properties["name"],
            objects=properties["objects"],
            permonst=properties["permonst"],
            quantity=properties["quantity"],
            beatitude=properties["beatitude"],
            erosion=properties["erosion"],
            enchantment=properties["enchantment"],
            shop_status=properties["shop_status"],
            shop_price=properties["shop_price"],
            item_class=properties["item_class"],
            equipped=properties["equipped"],
            at_ready=properties["at_ready"],
        )

    def update_from_text(self, text):
        properties = Item.parse_item_text(text)
        self.text = text
        self.name = properties["name"]
        self.objects = properties["objects"]
        self.permonst = properties["permonst"]
        self.quantity = properties["quantity"]
        self.beatitude = properties["beatitude"]
        self.erosion = properties["erosion"]
        self.enchantment = properties["enchantment"]
        self.shop_status = properties["shop_status"]
        self.shop_price = properties["shop_price"]
        self.item_class = properties["item_class"]
        self.equipped = properties["equipped"]
        self.at_ready = properties["at_ready"]

    @staticmethod
    def parse_item_text(text):
        item_pattern = (
            # Core item properties
            r"^(?P<quantity>a|an|the|\d+)"
            r"(?P<empty> empty)?"
            r"(?:\s+(?P<beatitude>cursed|uncursed|blessed))?"
            # Erosion conditions
            r"(?P<erosion>(?:\s+"  # Start with space if there's a match
            r"(?:(?:very|thoroughly)\s+)?"  # Intensity modifiers
            r"(?:rusty|corroded|burnt|rotted)"
            r")*)"
            # Other conditions
            r"(?P<other_condition>(?:\s+"  # Start with space if there's a match
            r"(?:rustproof|poisoned|"
            r"partly eaten|partly used|diluted|unlocked|locked|wet|greased)"
            r")*)"
            # Item details
            r"(?:\s+(?P<enchantment>[+-]\d+))?"  # Space before enchantment
            r"\s+(?P<name>[a-zA-z0-9-!'# ]+)"  # Required space before name
            # Optional information
            r"(?:\s+\((?P<uses>[0-9]+:[0-9]+|no charge)\))?"
            r"(?:\s+\((?P<info>[a-zA-Z0-9; ]+(?:,\s+(?:flickering|gleaming|glimmering))?[a-zA-Z0-9; ]*)\))?"
            # Shop information
            r"(?:\s+\((?P<shop_status>for sale|unpaid),\s+"
            r"(?:\d+\s+aum,\s+)?(?P<shop_price>\d+[a-zA-Z-]+|no charge)\))?"
            r"$"
        )

        def clean_matches(match_dict):
            """Clean up the matched groups by removing None and extra spaces"""
            if not match_dict:
                return None

            return {key: value.strip() if value else "" for key, value in match_dict.items()}

        # Usage:
        matches = re.match(item_pattern, text)
        if matches:
            item_info = clean_matches(matches.groupdict())

            name = item_info["name"]
            quantity = ItemQuantity.from_str(item_info["quantity"])
            beatitude = ItemBeatitude.from_str(item_info["beatitude"])
            erosion = ItemErosion.from_str(item_info["erosion"])
            enchantment = ItemEnchantment.from_str(item_info["enchantment"])
            shop_status = ShopStatus.from_str(item_info["shop_status"])
            shop_price = ShopPrice.from_str(item_info["shop_price"])

            # some items can be identified from name
            if name in ["potion of holy water", "potions of holy water"]:
                name = "potion of water"
                beatitude = ItemBeatitude.BLESSED
            elif name in ["potion of unholy water", "potions of unholy water"]:
                name = "potion of water"
                beatitude = ItemBeatitude.CURSED
            elif name in ["gold piece", "gold pieces"]:
                beatitude = ItemBeatitude.UNCURSED

            if (
                item_info["info"]
                in {"being worn", "being worn; slippery", "wielded", "chained to you", "on right hand", "on left hand"}
                or item_info["info"].startswith("weapon in ")
                or item_info["info"].startswith("tethered weapon in ")
            ):
                equipped = True
                at_ready = False
            elif item_info["info"] in {"at the ready", "in quiver", "in quiver pouch", "lit"}:
                equipped = False
                at_ready = True
            elif item_info["info"] in {"", "alternate weapon; not wielded", "alternate weapon; notwielded"}:
                equipped = False
                at_ready = False
            else:
                assert False, item_info["info"]

            permonst = None
            item_class = None

            if name.endswith(" corpse") or name.endswith(" corpses"):
                name = Item.make_singular(name)
                name = name.removesuffix(" corpse")
                name = name.removeprefix("an ")
                name = name.removeprefix("a ")
                permonst = name_to_monsters[name]
                item_class = ItemClass.CORPSE
                name = "corpse"
            elif (
                name.startswith("statue of ")
                or name.startswith("statues of ")
                or name.startswith("historic statue of ")
                or name.startswith("historic statues of ")
            ):
                name = Item.make_singular(name)
                name = name.removeprefix("historic statue of ")
                name = name.removeprefix("statue of ")
                name = name.removeprefix("an ")
                name = name.removeprefix("a ")
                permonst = name_to_monsters[name]
                item_class = ItemClass.STATUE
                name = "statue"
            elif name.startswith("figurine of ") or name.startswith("figurines of "):
                name = Item.make_singular(name)
                name = name.removeprefix("figurine of ")
                name = name.removeprefix("an ")
                name = name.removeprefix("a ")
                permonst = name_to_monsters[name]
                name = "figurine"
            elif name.startswith("tin of ") or name.startswith("tins of "):
                name = Item.make_singular(name)
                name = name.removeprefix("tin of ")
                if "meat" in name:
                    name = name.removesuffix(" meat")
                    permonst = name_to_monsters[name]
                elif "spinach" in name:
                    pass
                name = "tin"
            elif name.endswith(" egg") or name.endswith(" eggs"):
                name = Item.make_singular(name)
                name = name.removeprefix("an ")
                name = name.removeprefix("a ")
                permonst = name_to_monsters[name]
                name = "egg"

            # TODO: what about monsters (python?)
            name = Item.make_singular(name)
            name = Item.convert_from_japanese(name)

            # TODO objects
            objects = Item.name_to_objects(name)

            if item_class is None:
                item_class = ItemClass.from_oclass(ord(objects[0].oc_class))

            return dict(
                name=name,
                objects=objects,
                permonst=permonst,
                quantity=quantity,
                beatitude=beatitude,
                erosion=erosion,
                enchantment=enchantment,
                shop_status=shop_status,
                shop_price=shop_price,
                item_class=item_class,
                equipped=equipped,
                at_ready=at_ready,
            )
        else:
            raise ValueError()

    @staticmethod
    def make_singular(plural_word):
        # exceptions
        if plural_word in ["looking glass"]:
            return plural_word

        # Attempt to convert the plural word to singular
        singular = p.singular_noun(plural_word)
        # If the word is already singular or cannot be converted, return the original word
        return singular if singular else plural_word

    @staticmethod
    def convert_from_japanese(japanese_name):
        convert_from_japanese = {
            "wakizashi": "short sword",
            "ninja-to": "broadsword",
            "nunchaku": "flail",
            "naginata": "glaive",
            "osaku": "lock pick",
            "koto": "wooden harp",
            "shito": "knife",
            "tanko": "plate mail",
            "kabuto": "helmet",
            "yugake": "pair of leather gloves",
            "gunyoki": "food ration",
            "sake": "booze",
        }
        words = japanese_name.split(" ")
        converted_words = [convert_from_japanese.get(word, word) for word in words]
        return " ".join(converted_words)

    @staticmethod
    def name_to_objects(name):
        objects = NAME_TO_OBJECTS[name]

        if len(objects) == 0:
            print(1)

        assert len(objects) >= 1, f"There should be at least one object matching name: {name}"

        lst = [ItemClass(ord(obj.oc_class)) for obj in objects]
        assert all(x == lst[0] for x in lst), "Objects don't have the same category"

        return objects

    def __str__(self):
        text = []
        text.append(f"{chr(self.letter)})" if self.letter else "")
        text.append(str(self.quantity))
        text.append(str(self.beatitude))
        text.append(str(self.erosion))
        text.append(str(self.enchantment))

        if self.item_class in [ItemClass.CORPSE, ItemClass.STATUE]:
            text.append(f"{self.permonst.mname} {self.name}")
        else:
            text.append(self.name)

        text.append(str(self.shop_status))
        if self.shop_status in [ShopStatus.UNPAID, ShopStatus.FOR_SALE]:
            text.append(str(self.shop_price))

        if self.equipped:
            text.append("(equipped)")
        if self.at_ready:
            text.append("(at ready)")

        return " ".join([t for t in text if t])

    def __repr__(self):
        return str(self)

    """
    WEAPON
    """

    @property
    def weapon_class(self) -> Optional[WeaponClass]:
        if self.item_class == ItemClass.WEAPON:
            return WeaponClass.from_oc_skill(self.objects[0].oc_skill)

    @property
    def is_weapon(self) -> bool:
        if not self.item_class == ItemClass.WEAPON:
            return False

        return self.weapon_class == WeaponClass.WEAPON

    @property
    def is_launcher(self):
        if not self.item_class == ItemClass.WEAPON:
            return False

        return self.weapon_class == WeaponClass.BOW

    @property
    def is_projectile(self) -> bool:
        if not self.item_class == ItemClass.WEAPON:
            return False

        return self.weapon_class == WeaponClass.PROJECTILE

    def can_shoot_projectile(self, projectile: Item):
        if not self.is_launcher:
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
        # TODO: sling ammo
        return self.is_projectile

    @property
    def is_thrown_projectile(self):
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
    def armor_class(self):
        if self.item_class == ItemClass.ARMOR:
            return ArmorClass(self.objects[0].oc_armcat)

    @property
    def arm_bonus(self):
        return self.objects[0].a_ac + self.enchantment.value - min(self.erosion.value, self.objects[0].a_ac)

    """
    COMESTIBLES
    """

    @property
    def is_corpse(self):
        return self.item_class == ItemClass.CORPSE

    @property
    def is_food(self):
        return self.item_class == ItemClass.COMESTIBLES

    @property
    def nutrition(self):
        """Calculate base nutrition of a food object."""

        # Determine base nutrition value based on object type
        # NOTE: skipped globby and special cases for certain food types
        if self.item_class == ItemClass.CORPSE:
            nut = self.permonst.cnutrit
        else:
            nut = self.objects[0].oc_nutrition

        return self.quantity.value * nut

    """
    TOOLS
    """

    # TODO:
    @property
    def tool_class(self):
        if self.item_class == ItemClass.TOOL:
            return ToolClass(1)

    @property
    def is_key(self):
        return self.item_class == ItemClass.TOOL and self.name in ["skeleton key", "lock pick", "credit card"]

    """
    GEMS
    """

    # TODO:
    @property
    def gem_class(self):
        if self.item_class == ItemClass.GEM:
            return GemClass(self.objects[0].oc_tough)

    @property
    def weight(self):
        wt = self.objects[0].oc_weight

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
        if self.item_class == ItemClass.CORPSE:
            return self.quantity.value * self.permonst.cwt
            # NOTE: we ignore partly eaten

        # coin
        # } else if (obj->oclass == COIN_CLASS) {
        #     return (int) ((obj->quan + 50L) / 100L);
        if self.item_class == ItemClass.COIN:
            return (self.quantity.value + 50) // 100

        # heavy iron ball
        # } else if (obj->otyp == HEAVY_IRON_BALL && obj->owt != 0) {
        #     return (int) obj->owt; /* kludge for "very" heavy iron ball */
        # TODO:

        if wt:
            return self.quantity.value * wt
        else:
            return (self.quantity.value + 1) >> 1

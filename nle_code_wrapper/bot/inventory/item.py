from __future__ import annotations

from typing import Optional

from nle import nethack as nh

from nle_code_wrapper.bot.inventory.item_database import ItemClass
from nle_code_wrapper.bot.inventory.properties import (
    ArmorClass,
    GemClass,
    ItemBeatitude,
    ItemCategory,
    ItemEnchantment,
    ItemErosion,
    ItemQuantity,
    ShopPrice,
    ShopStatus,
    ToolClass,
    WeaponClass,
)


class Item:
    def __init__(
        self,
        text: str,
        item_class: ItemClass,
        letter: Optional[int] = None,
        **properties,
    ):
        self.text = text
        self.letter = letter
        self.item_class = item_class
        self.update_properties(**properties)

    def update_properties(
        self,
        name: str,
        named: str,
        permonst,
        item_category: ItemCategory,
        quantity: ItemQuantity,
        beatitude: ItemBeatitude,
        erosion: ItemErosion,
        enchantment: ItemEnchantment,
        shop_status: ShopStatus,
        shop_price: ShopPrice,
        equipped: bool,
        at_ready: bool,
    ):
        self._name = name
        self.named = named
        self.permonst = permonst
        self.item_category = item_category if item_category else self.item_class.item_category

        self.quantity = quantity
        self.beatitude = beatitude
        self.erosion = erosion
        self.enchantment = enchantment
        self.shop_status = shop_status
        self.shop_price = shop_price

        self.equipped = equipped
        self.at_ready = at_ready

    @property
    def name(self):
        if self.is_identified:
            return str(self.item_class)
        else:
            return self._name

    def __str__(self):
        text = []
        text.append(f"{chr(self.letter)})" if self.letter else "")
        text.append(str(self.quantity))
        text.append(str(self.beatitude))
        text.append(str(self.erosion))
        text.append(str(self.enchantment))

        if self.item_category in [ItemCategory.CORPSE, ItemCategory.STATUE]:
            text.append(f"{self.permonst.mname} {self.name}")
        else:
            text.append(self.name)

        if self.named:
            text.append(f"named {self.named}")

        text.append(str(self.shop_status))
        if self.shop_status in [ShopStatus.UNPAID, ShopStatus.FOR_SALE]:
            text.append(str(self.shop_price))

        if self.equipped:
            text.append("(equipped)")
        if self.at_ready:
            text.append("(at ready)")
        if self.item_class.engraved:
            text.append("(engraved)")

        return " ".join([t for t in text if t])

    def __repr__(self):
        return str(self)

    @property
    def is_identified(self):
        return self.item_class.is_identified

    @property
    def object(self):
        return nh.objclass(nh.glyph_to_obj(self.item_class.candidate_ids[0]))

    """
    WEAPON
    """

    @property
    def weapon_class(self) -> Optional[WeaponClass]:
        if self.item_category == ItemCategory.WEAPON:
            return WeaponClass.from_oc_skill(self.object.oc_skill)

    @property
    def is_weapon(self) -> bool:
        return self.weapon_class == WeaponClass.WEAPON

    @property
    def is_launcher(self):
        return self.weapon_class == WeaponClass.BOW

    @property
    def is_projectile(self) -> bool:
        return self.weapon_class == WeaponClass.PROJECTILE

    def can_shoot_projectile(self, projectile: Item):
        if not self.is_launcher:
            return False

        arrows = ["arrow", "elven arrow", "orcish arrow", "silver arrow", "ya"]

        if self.name == "crossbow":
            return projectile.name == "crossbow bolt"

        if self.name == "sling":
            return projectile.gem_class == GemClass.ROCK

        bows = ["bow", "long bow", "elven bow", "orcish bow", "yumi"]
        if self.name in bows:
            return projectile.name in arrows

    @property
    def is_firing_projectile(self):
        return self.is_projectile or self.gem_class == GemClass.ROCK

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
        if self.item_category == ItemCategory.ARMOR:
            return ArmorClass(self.object.oc_armcat)

    @property
    def arm_bonus(self):
        return self.object.a_ac + self.enchantment.value - min(self.erosion.value, self.object.a_ac)

    """
    COMESTIBLES
    """

    @property
    def is_corpse(self):
        return self.item_category == ItemCategory.CORPSE

    @property
    def is_food(self):
        return self.item_category == ItemCategory.COMESTIBLES

    @property
    def nutrition(self):
        """Calculate base nutrition of a food object."""

        # Determine base nutrition value based on object type
        # NOTE: skipped special cases for certain food types
        if self.item_category == ItemCategory.CORPSE:
            globby = "ooze" in self._name
            if globby:
                nut = self.weight
            else:
                nut = self.permonst.cnutrit
        else:
            nut = self.object.oc_nutrition

        return self.quantity.value * nut

    """
    TOOLS
    """

    # TODO:
    @property
    def tool_class(self):
        if self.item_category == ItemCategory.TOOL:
            return ToolClass.from_name(self.name)

    @property
    def is_key(self):
        return self.tool_class == ToolClass.KEY

    """
    GEMS
    """

    @property
    def gem_class(self):
        if self.item_category == ItemCategory.GEM:
            return GemClass.from_name(self.name)

    @property
    def weight(self):
        wt = self.object.oc_weight

        # NOTE: partly_eaten (food, corpses), candelabrum

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
        if self.item_category == ItemCategory.CORPSE:
            # handle globby
            globby = "ooze" in self._name
            if globby:
                if "very large" in self.text:
                    return 500
                elif "large" in self.text:
                    return 300
                else:
                    return 100
            else:
                return self.quantity.value * self.permonst.cwt
            # NOTE: we ignore partly eaten

        # coin
        # } else if (obj->oclass == COIN_CLASS) {
        #     return (int) ((obj->quan + 50L) / 100L);
        if self.item_category == ItemCategory.COIN:
            return (self.quantity.value + 50) // 100

        # heavy iron ball
        # } else if (obj->otyp == HEAVY_IRON_BALL && obj->owt != 0) {
        #     return (int) obj->owt; /* kludge for "very" heavy iron ball */
        # TODO:

        if wt:
            return self.quantity.value * wt
        else:
            return (self.quantity.value + 1) >> 1

from __future__ import annotations

import re
from typing import Dict, List

from nle_code_wrapper.bot.inventory.item import Item
from nle_code_wrapper.bot.inventory.item_database import ItemDatabase
from nle_code_wrapper.bot.inventory.item_parser import ItemParser
from nle_code_wrapper.bot.inventory.properties import ArmorClass, ItemCategory


class Inventory:
    def __init__(self):
        self.items: Dict[int, Item] = {}
        self.item_parser = ItemParser()
        self.inventory_categories = {
            "coins": [ItemCategory.COIN],
            "amulets": [ItemCategory.AMULET],
            "weapons": [ItemCategory.WEAPON],
            "armor": [ItemCategory.ARMOR],
            "comestibles": [
                ItemCategory.COMESTIBLES,
                ItemCategory.CORPSE,
            ],
            "scrolls": [ItemCategory.SCROLL],
            "spellbooks": [ItemCategory.SPELLBOOK],
            "potions": [ItemCategory.POTION],
            "rings": [ItemCategory.RING],
            "wands": [ItemCategory.WAND],
            "tools": [
                ItemCategory.TOOL,
                ItemCategory.GEM,
                ItemCategory.ROCK,
                ItemCategory.BALL,
                ItemCategory.CHAIN,
                ItemCategory.VENOM,
                ItemCategory.STATUE,
            ],
        }

    def update(self, inv_strs, inv_letters, inv_oclasses, inv_glyphs, item_database: ItemDatabase):
        old_keys = set(self.items.keys())
        new_keys = set()
        for i in range(len(inv_strs)):
            letter = inv_letters[i]
            inv_str = inv_strs[i]

            if letter == 0:
                break

            new_keys.add(letter)

            text = bytes(inv_str).decode("latin-1").strip("\0")
            properties = self.item_parser(text)

            if letter in self.items:
                self.items[letter].update_properties(**properties)
            else:
                self.items[letter] = Item(
                    text=text,
                    letter=letter,
                    item_class=item_database.get(properties["name"]),
                    **properties,
                )

        unused_keys = old_keys.difference(new_keys)
        for key in unused_keys:
            del self.items[key]

    def __getitem__(self, key) -> List[Item]:
        category = self.inventory_categories[key]
        return [item for item in self.items.values() if item.item_category in category]

    @property
    def inventory(self):
        return {key: self[key] for key in self.inventory_categories.keys()}

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return "Inventory:\n\t" + "\n\t".join(
            f"{key}:\n\t\t" + "\n\t\t".join(str(item) for item in category)
            for key, category in self.inventory.items()
            if category
        )

    def __repr__(self):
        return str(self)

    @property
    def main_hand(self):
        wielded_weapon = [weapon for weapon in self["weapons"] if weapon.equipped]
        return wielded_weapon[0] if wielded_weapon else None

    @property
    def off_hand(self):
        wielded_weapon = [weapon for weapon in self["weapons"] if weapon.at_ready]
        return wielded_weapon[0] if wielded_weapon else None

    @property
    def worn_armor_by_type(self):
        """Returns a dictionary of worn armor items indexed by their ArmorClass."""
        worn_armor = [armor for armor in self["armor"] if armor.equipped]
        return {
            armor_class: next((armor for armor in worn_armor if armor.armor_class == armor_class), None)
            for armor_class in ArmorClass
        }

    @property
    def suit(self):
        return self.worn_armor_by_type[ArmorClass.SUIT]

    @property
    def shield(self):
        return self.worn_armor_by_type[ArmorClass.SHIELD]

    @property
    def helm(self):
        return self.worn_armor_by_type[ArmorClass.HELM]

    @property
    def gloves(self):
        return self.worn_armor_by_type[ArmorClass.GLOVES]

    @property
    def boots(self):
        return self.worn_armor_by_type[ArmorClass.BOOTS]

    @property
    def cloak(self):
        return self.worn_armor_by_type[ArmorClass.CLOAK]

    @property
    def shirt(self):
        return self.worn_armor_by_type[ArmorClass.SHIRT]


if __name__ == "__main__":
    import gym
    import nle

    env = gym.make("NetHackScore-v0", character="@")
    for i in range(100):
        env.seed(i)
        obs = env.reset()

        inv_glyphs = obs["inv_glyphs"]
        inv_letters = obs["inv_letters"]
        inv_oclasses = obs["inv_oclasses"]
        inv_strs = obs["inv_strs"]

        inventory = Inventory()
        item_database = ItemDatabase()
        inventory.update(inv_strs, inv_letters, inv_oclasses, inv_glyphs, item_database)
        inventory.main_hand
        inventory.off_hand
        inventory.helm
        print(inventory)

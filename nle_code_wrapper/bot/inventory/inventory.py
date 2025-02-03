from __future__ import annotations

from typing import Dict, List

from nle_code_wrapper.bot.inventory.item import Item
from nle_code_wrapper.bot.inventory.properties import ArmorClass, ItemClass


class Inventory:
    def __init__(self, inv_strs, inv_letters, inv_oclasses, inv_glyphs):
        self.items = []
        for i in range(len(inv_strs)):
            letter = inv_letters[i]
            inv_str = inv_strs[i]

            if letter == 0:
                break

            text = bytes(inv_str).decode("latin-1").strip("\0")
            item = Item.from_text(text, letter=letter)
            item.weapon_class
            self.items.append(item)

        self.inventory: Dict[str, List[Item]] = {}
        inventory_classes = {
            "coins": [ItemClass.COIN],
            "amulets": [ItemClass.AMULET],
            "weapons": [ItemClass.WEAPON],
            "armor": [ItemClass.ARMOR],
            "comestibles": [
                ItemClass.COMESTIBLES,
                ItemClass.CORPSE,
            ],
            "scrolls": [ItemClass.SCROLL],
            "spellbooks": [ItemClass.SPELLBOOK],
            "potions": [ItemClass.POTION],
            "rings": [ItemClass.RING],
            "wands": [ItemClass.WAND],
            "tools": [
                ItemClass.TOOL,
                ItemClass.GEM,
                ItemClass.ROCK,
                ItemClass.BALL,
                ItemClass.CHAIN,
                ItemClass.VENOM,
                ItemClass.STATUE,
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

        inventory = Inventory(inv_strs, inv_letters, inv_oclasses, inv_glyphs)
        inventory.main_hand
        inventory.off_hand
        inventory.helm
        print(inventory)

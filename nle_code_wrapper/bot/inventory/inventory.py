from __future__ import annotations

from typing import Dict, List

from nle_utils.item import ArmorType, ItemClasses

from nle_code_wrapper.bot.inventory.item import Item


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

import numpy as np
from nle_utils.item import ItemBeatitude, ItemClasses, ItemEnchantment, ItemShopStatus


class Item:
    def __init__(
        self,
        letter: int,
        name: np.ndarray,
        oclass: int,
        glyph: int,
        shop_status: int = None,
        value: int = None,
        weight: int = None,
    ):
        self.letter = chr(letter)
        self.name = "".join(map(chr, name)).rstrip("\x00")
        self.item_class = ItemClasses(oclass)
        self.glyph = glyph

        self.shop_status = ItemShopStatus(shop_status) if shop_status is not None else None
        self.value = value
        self.weight = weight

    @property
    def beatitude(self):
        if "blessed" in self.name:
            return ItemBeatitude.BLESSED
        elif "uncursed" in self.name:
            return ItemBeatitude.UNCURSED
        elif "cursed" in self.name:
            return ItemBeatitude.CURSED
        else:
            return ItemBeatitude.UNKNOWN

    @property
    def in_use(self):
        if "(" in self.name:
            return True
        else:
            return False

    @property
    def quantity(self):
        if self.name.split(" ")[0].isdigit():
            return int(self.name.split(" ")[0])
        else:
            return 1

    @property
    def enchantment(self):
        if "+" in self.name:
            ench = int(self.name.split("+")[1].split(" ")[0])
        elif "-" in self.name:
            ench = int(self.name.split("-")[1].split(" ")[0])
        else:
            ench = None
        return ItemEnchantment(ench)

    def __str__(self):
        return f"{self.letter}) {self.name}"


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

        self.inventory = {}
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

    def __getitem__(self, key):
        return self.items[key]

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

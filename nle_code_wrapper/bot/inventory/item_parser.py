import re

import inflect

from nle_code_wrapper.bot.inventory.objects import name_to_monsters
from nle_code_wrapper.bot.inventory.properties import (
    ItemBeatitude,
    ItemCategory,
    ItemEnchantment,
    ItemErosion,
    ItemQuantity,
    ShopPrice,
    ShopStatus,
)

p = inflect.engine()


class ItemParser:
    # Constants
    SPECIAL_ITEMS = {
        "potion of holy water": ("potion of water", ItemBeatitude.BLESSED),
        "potions of holy water": ("potion of water", ItemBeatitude.BLESSED),
        "potion of unholy water": ("potion of water", ItemBeatitude.CURSED),
        "potions of unholy water": ("potion of water", ItemBeatitude.CURSED),
        "gold piece": (None, ItemBeatitude.UNCURSED),
        "gold pieces": (None, ItemBeatitude.UNCURSED),
    }

    EQUIPPED_STATES = {
        "being worn": (True, False),
        "being worn; slippery": (True, False),
        "wielded": (True, False),
        "chained to you": (True, False),
        "on right hand": (True, False),
        "on left hand": (True, False),
        "on right foreclaw": (True, False),
        "on left foreclaw": (True, False),
        "on right forehoof": (True, False),
        "on left forehoof": (True, False),
        "at the ready": (False, True),
        "in quiver": (False, True),
        "in quiver pouch": (False, True),
        "lit": (False, True),
        "": (False, False),
        "alternate weapon; not wielded": (False, False),
        "alternate weapon; notwielded": (False, False),
    }

    def __init__(self):
        self.item_pattern = self._compile_item_pattern()

    def _compile_item_pattern(self):
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
            r"partly eaten|partly used|diluted|unlocked|locked|broken|wet|greased)"
            r")*)"
            # Item details
            r"(?:\s+(?P<enchantment>[+-]\d+))?"  # Space before enchantment
            r"\s+(?P<name>[a-zA-z0-9-!'# ]+)"  # Required space before name
            # Optional information
            r"(?:\s+\((?P<uses>[0-9]+:[0-9]+|no charge)\))?"
            r"(?:\s+\((?P<info>[a-zA-Z0-9; ]+(?:,\s+(?:flickering|gleaming|glimmering))?[a-zA-Z0-9; ]*)\))?"
            # Shop information
            r"(?:\s+\((?P<shop_status>for sale|unpaid),\s+"  # Matches shop status
            r"(?:\d+\s+aum,\s+)?(?P<shop_price>\d+)\s+zorkmids\))?"  # Matches shop price and currency
            r"$"
        )

        return re.compile(item_pattern)

    def __call__(self, text):
        matches = re.match(self.item_pattern, text)
        if not matches:
            return None

        item_info = self._clean_matches(matches.groupdict())

        # Parse basic properties
        parsed_item = self._parse_basic_properties(item_info)

        # Handle special cases
        self._handle_special_items(parsed_item)

        # Parse equipment status
        self._parse_equipment_status(parsed_item, item_info)

        # Parse creature-related items
        self._parse_creature_items(parsed_item)

        return parsed_item

    def _clean_matches(self, match_dict):
        """Clean up the matched groups by removing None and extra spaces"""
        return {key: value.strip() if value else "" for key, value in match_dict.items()}

    def _parse_basic_properties(self, item_info):
        return {
            "name": item_info["name"],
            "quantity": ItemQuantity.from_str(item_info["quantity"]),
            "beatitude": ItemBeatitude.from_str(item_info["beatitude"]),
            "erosion": ItemErosion.from_str(item_info["erosion"]),
            "enchantment": ItemEnchantment.from_str(item_info["enchantment"]),
            "shop_status": ShopStatus.from_str(item_info["shop_status"]),
            "shop_price": ShopPrice.from_str(item_info["shop_price"]),
            "permonst": None,
            "item_category": None,
        }

    def _handle_special_items(self, parsed_item):
        special_item = self.SPECIAL_ITEMS.get(parsed_item["name"])
        if special_item:
            new_name, beatitude = special_item
            if new_name:
                parsed_item["name"] = new_name
            parsed_item["beatitude"] = beatitude

    def _parse_equipment_status(self, parsed_item, item_info):
        info = item_info["info"]
        if info.startswith("weapon in ") or info.startswith("tethered weapon in "):
            parsed_item["equipped"] = True
            parsed_item["at_ready"] = False
        else:
            equipped, at_ready = self.EQUIPPED_STATES.get(info, (None, None))

            if "foreclaw" in info:
                print(1)

            if equipped is None:
                raise ValueError(f"Unknown equipment status: {info}")
            parsed_item["equipped"] = equipped
            parsed_item["at_ready"] = at_ready

    def _make_singular(self, plural_word):
        # exceptions
        if plural_word in ["looking glass", "aklys"]:
            return plural_word

        if plural_word.startswith("scrolls"):
            plural_word = plural_word.replace("scrolls", "scroll", 1)

        # Attempt to convert the plural word to singular
        singular = p.singular_noun(plural_word)
        # If the word is already singular or cannot be converted, return the original word
        return singular if singular else plural_word

    def _convert_from_japanese(self, japanese_name):
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

    def _handle_corpse(self, parsed_item):
        """Handle corpse items"""
        name = parsed_item["name"]
        name = self._make_singular(name)
        name = name.removesuffix(" corpse")
        name = name.removeprefix("an ")
        name = name.removeprefix("a ")
        parsed_item.update({"permonst": name_to_monsters[name], "item_category": ItemCategory.CORPSE, "name": "corpse"})

    def _handle_statue(self, parsed_item):
        """Handle statue items"""
        name = parsed_item["name"]
        name = self._make_singular(name)
        name = name.removeprefix("historic statue of ")
        name = name.removeprefix("statue of ")
        name = name.removeprefix("an ")
        name = name.removeprefix("a ")
        parsed_item.update({"permonst": name_to_monsters[name], "item_category": ItemCategory.STATUE, "name": "statue"})

    def _handle_figurine(self, parsed_item):
        """Handle figurine items"""
        name = parsed_item["name"]
        name = self._make_singular(name)
        name = name.removeprefix("figurine of ")
        name = name.removeprefix("an ")
        name = name.removeprefix("a ")
        parsed_item.update({"permonst": name_to_monsters[name], "name": "figurine"})

    def _handle_tin(self, parsed_item):
        """Handle tin items"""
        name = parsed_item["name"]
        name = self._make_singular(name)
        name = name.removeprefix("tin of ")
        if "meat" in name:
            name = name.removesuffix(" meat")
            parsed_item["permonst"] = name_to_monsters[name]
        parsed_item["name"] = "tin"

    def _handle_egg(self, parsed_item):
        """Handle egg items"""
        name = parsed_item["name"]
        name = self._make_singular(name)
        name = name.removeprefix("an ")
        name = name.removeprefix("a ")
        parsed_item.update({"permonst": name_to_monsters[name], "name": "egg"})

    def _matches_any_suffix(self, name, suffixes):
        """Helper method to check if name starts/ends with any of the given suffixes"""
        return any(name.endswith(suffix) for suffix in suffixes) or any(name.startswith(suffix) for suffix in suffixes)

    def _parse_creature_items(self, parsed_item):
        name = parsed_item["name"]

        creature_item_handlers = {
            (" corpse", " corpses"): self._handle_corpse,
            ("statue of ", "statues of "): self._handle_statue,
            ("figurine of ", "figurines of "): self._handle_figurine,
            ("tin of ", "tins of "): self._handle_tin,
            (" egg", " eggs"): self._handle_egg,
        }

        for suffixes, handler in creature_item_handlers.items():
            if self._matches_any_suffix(name, suffixes):
                handler(parsed_item)
                break

        parsed_item["name"] = self._make_singular(parsed_item["name"])
        parsed_item["name"] = self._convert_from_japanese(parsed_item["name"])


if __name__ == "__main__":
    parser = ItemParser()
    item = parser("a blessed +1 sword (being worn)")
    print(item)

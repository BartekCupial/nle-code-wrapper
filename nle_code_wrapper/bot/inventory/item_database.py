from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from nle_code_wrapper.bot.inventory.objects import GLYPH_TO_OBJ_NAME, NAME_TO_GLYPHS
from nle_code_wrapper.bot.inventory.properties import ItemCategory


@dataclass
class ItemClass:
    """Represents a single item entry in the database"""

    name: str
    item_category: ItemCategory
    possible_items: List[int] = None

    def __post_init__(self):
        if self.possible_items is None:
            self.possible_items = []

    @classmethod
    def from_name_to_glyphs(cls, name: str, glyphs: List[int]) -> ItemClass:
        """Creates an ItemClass from a name and list of glyphs"""
        item_categories = [ItemCategory.from_glyph(glyph) for glyph in glyphs]

        if not item_categories or not all(x == item_categories[0] for x in item_categories):
            raise ValueError("Objects must have the same category")

        return cls(name=name, item_category=item_categories[0], possible_items=glyphs.copy())

    @property
    def is_unambiguous(self) -> bool:
        """Returns True if the item has exactly one possible interpretation"""
        return len(self.possible_items) == 1

    def get_possible_names(self) -> List[str]:
        """Returns list of possible object names for this item"""
        return [GLYPH_TO_OBJ_NAME[glyph] for glyph in self.possible_items]

    def __str__(self) -> str:
        if self.is_unambiguous:
            return self.name
        return f"{self.name}: {'; '.join(self.get_possible_names())}"


class ItemDatabase:
    """Database containing all possible items and their properties"""

    def __init__(self):
        self.items: Dict[str, ItemClass] = self._initialize_items()

    def _initialize_items(self) -> Dict[str, ItemClass]:
        """Initialize the database from NAME_TO_GLYPHS mapping"""
        return {name: ItemClass.from_name_to_glyphs(name, glyphs) for name, glyphs in NAME_TO_GLYPHS.items()}

    def __getitem__(self, key: str) -> ItemClass:
        return self.items[key]

    def get(self, key: str, default=None):
        if key in self.items:
            return self[key]
        else:
            return default

    def __str__(self) -> str:
        return "\n".join(str(item) for item in self.items.values())

    def get_items_by_category(self, item_category: ItemCategory) -> List[ItemClass]:
        """Returns all items of a specific ItemCategory"""
        return [item for item in self.items.values() if item.item_category == item_category]


def main():
    database = ItemDatabase()
    print(database)

    # Example of getting items by class
    weapons = database.get_items_by_class(ItemCategory.WEAPON)
    print("\nWeapons:", len(weapons))


if __name__ == "__main__":
    main()

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List

from nle_code_wrapper.bot.inventory.objects import GLYPH_TO_OBJ_NAME, NAME_TO_GLYPHS
from nle_code_wrapper.bot.inventory.properties import ItemCategory

if TYPE_CHECKING:
    from nle_code_wrapper.bot.inventory.item import Item


def flatten_single_element_list(list_of_lists):
    # Assert that input is a list
    assert isinstance(list_of_lists, list), "Input must be a list"

    # Check if each inner list has exactly one element
    for inner_list in list_of_lists:
        assert isinstance(inner_list, list), "Each element must be a list"
        assert len(inner_list) == 1, f"Each inner list must contain exactly one element, got {len(inner_list)} elements"

    # Flatten the list using list comprehension
    return [item for sublist in list_of_lists for item in sublist]


@dataclass
class ItemClass:
    """Represents a single item entry in the database"""

    name: str
    item_category: ItemCategory
    candidate_ids: List[int] = None
    engraved: bool = False

    def __post_init__(self):
        if self.candidate_ids is None:
            self.candidate_ids = []

    @classmethod
    def create_from_identifiers(cls, name: str, item_ids: List[int]) -> ItemClass:
        """Creates an ItemClass from a display name and list of item identifiers"""
        categories = [ItemCategory.from_glyph(glyph) for glyph in item_ids]

        if not categories or not all(x == categories[0] for x in categories):
            raise ValueError("Objects must have the same category")

        return cls(name=name, item_category=categories[0], candidate_ids=item_ids.copy())

    @property
    def is_identified(self) -> bool:
        """Returns True if the item has exactly one possible identification"""
        return len(self.candidate_ids) == 1

    def get_candidate_names(self) -> List[str]:
        """Returns list of possible item names based on candidate IDs"""
        return [GLYPH_TO_OBJ_NAME[item_id] for item_id in self.candidate_ids]

    def __str__(self) -> str:
        if self.is_identified:
            return "".join(self.get_candidate_names())
        return f"{self.name}: {'; '.join(self.get_candidate_names())}"

    def update_candidates(self, new_candidate_ids: List[int]):
        """Updates candidate IDs to intersection of current and new possibilities"""
        if not self.candidate_ids:
            self.candidate_ids = new_candidate_ids.copy()
        else:
            self.candidate_ids = [id for id in self.candidate_ids if id in new_candidate_ids]

    def remove_candidate(self, item_id: int):
        if item_id in self.candidate_ids and len(self.candidate_ids) > 1:
            self.candidate_ids.remove(item_id)


class ItemDatabase:
    """Registry containing all possible items and their properties"""

    def __init__(self):
        self.item_classes: Dict[str, ItemClass] = self._initialize_records()

    def _initialize_records(self) -> Dict[str, ItemClass]:
        """Initialize the registry from NAME_TO_GLYPHS mapping"""
        return {name: ItemClass.create_from_identifiers(name, ids) for name, ids in NAME_TO_GLYPHS.items()}

    def __getitem__(self, key: str) -> ItemClass:
        return self.item_classes[key]

    def get(self, key: str, default=None):
        if key in self.item_classes:
            return self[key]
        else:
            return default

    def __str__(self) -> str:
        return "\n".join(str(item) for item in self.item_classes.values())

    def get_items_in_category(self, item_category: ItemCategory) -> List[ItemClass]:
        """Returns all items of a specific ItemCategory"""
        return [item for item in self.item_classes.values() if item.item_category == item_category]

    def update_item_candidates(self, item_class: ItemClass, new_candidate_ids: List[int]):
        new_candidate_ids = flatten_single_element_list(new_candidate_ids)
        item_class.update_candidates(new_candidate_ids)
        if item_class.is_identified:
            self.propagate_identification(item_class)

    def propagate_identification(self, item_class: ItemClass):
        category_items = self.get_items_in_category(item_class.item_category)
        for inventory_item in category_items:
            inventory_item.remove_candidate(item_class.candidate_ids[0])


def main():
    database = ItemDatabase()
    print(database)

    # Example of getting items by class
    weapons = database.get_items_in_category(ItemCategory.WEAPON)
    print("\nWeapons:", len(weapons))


if __name__ == "__main__":
    main()

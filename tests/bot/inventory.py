import numpy as np
import pytest
from nle import nethack
from nle_utils.item import ItemClasses, ItemErosion

from nle_code_wrapper.bot.inventory import OBJECT_NAMES, Inventory, Item, arm_bonus, get_object


@pytest.mark.parametrize(
    "full_name,obj_class",
    [
        ("26 gold pieces", ItemClasses.COINS),
        ("a +1 long sword (weapon in hand)", ItemClasses.WEAPONS),
        ("a +1 lance (alternate weapon; not wielded)", ItemClasses.WEAPONS),
        ("a blessed +1 ring mail (being worn)", ItemClasses.ARMOR),
        ("an uncursed +0 helmet (being worn)", ItemClasses.ARMOR),
        ("an uncursed +0 small shield (being worn)", ItemClasses.ARMOR),
        ("an uncursed +0 pair of leather gloves (being worn)", ItemClasses.ARMOR),
        ("9 uncursed apples", ItemClasses.COMPESTIBLES),
        ("4 uncursed carrots", ItemClasses.COMPESTIBLES),
        ("an orcish helm", ItemClasses.ARMOR),
        ("a scroll labeled ELAM EBOW", ItemClasses.SCROLLS),
        ("an uncursed scroll of identify", ItemClasses.SCROLLS),
        ("a dark green potion", ItemClasses.POTIONS),
        ("green gem", ItemClasses.GEMS),
        ("dark green spellbok", ItemClasses.SPELLBOOKS),
    ],
)
def test_get_object(full_name, obj_class):
    get_object(full_name, obj_class)


@pytest.mark.parametrize(
    "full_name,expected",
    [
        ("rusty small shield", 1),
        ("very rusty corroded small shield", 2),
        ("thoroughly burnt very corroded small shield", 3),
        ("rusty rotted small shield", 1),
        ("very rusty thoroughly corroded small shield", 3),
        ("thoroughly burnt very corroded rusty small shield", 3),
    ],
)
def test_greatest_erosion(full_name, expected):
    assert ItemErosion.from_name(full_name).value == expected


@pytest.mark.parametrize(
    "full_name",
    [
        "arrow",
        "elven arrow",
        "runed arrow",
        "orcish arrow",
        "crude arrow",
        "silver arrow",
        "ya",
        "bamboo arrow",
        "crossbow bolt",
    ],
)
def test_item_firing_projectiles(full_name):
    item = Item(ord("a"), np.array([ord(c) for c in full_name]), ItemClasses.WEAPONS.value, 0)
    assert item.is_firing_projectile


@pytest.mark.parametrize(
    "full_name",
    [
        "boomerang",
        "dagger",
        "elven dagger",
        "runed dagger",
        "orcish dagger",
        "crude dagger",
        "silver dagger",
        "worm tooth",
        "crysknife",
        "knife",
        "athame",
        "scalpel",
        "stiletto",
        "dart",
        "shuriken",
        "throwing star",
    ],
)
def test_item_thrown_projectiles(full_name):
    item = Item(ord("a"), np.array([ord(c) for c in full_name]), ItemClasses.WEAPONS.value, 0)
    assert item.is_thrown_projectile


@pytest.mark.parametrize(
    "full_name,base_ac,enchantment,erosion,expected_bonus",
    [
        # Basic cases - no erosion
        ("leather armor", 2, 0, 0, 2),  # Base AC only
        ("leather armor", 2, 1, 0, 3),  # Base AC + enchantment
        # Erosion cases
        ("leather armor", 2, 0, 1, 1),  # Partial erosion
        ("leather armor", 2, 0, 2, 0),  # Full erosion
        ("leather armor", 2, 0, 3, 0),  # Over-erosion (should cap at AC)
        # Enchantment + erosion combinations
        ("leather armor", 2, 2, 1, 3),  # +2 enchant, 1 erosion
        ("plate mail", 7, -1, 1, 5),  # Negative enchant, partial erosion
        ("plate mail", 7, 3, 2, 8),  # High enchant, high erosion
        # Different armor types
        ("crystal plate mail", 7, 0, 0, 7),  # High AC armor
        ("Hawaiian shirt", 0, 0, 0, 0),  # Low AC armor
    ],
)
def test_arm_bonus(full_name, base_ac, enchantment, erosion, expected_bonus):
    # Create item with specified parameters
    obj = get_object(full_name, ItemClasses.ARMOR)
    bonus = arm_bonus(obj, enchantment, erosion)

    assert obj.a_ac == base_ac
    assert bonus == expected_bonus

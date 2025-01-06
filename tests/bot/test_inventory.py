import numpy as np
import pytest
from nle import nethack
from nle_utils.item import ItemClasses, ItemEnchantment, ItemErosion

from nle_code_wrapper.bot.inventory import GLYPH_TO_OBJECT, Item, arm_bonus


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
    for glyph, obj_dict in GLYPH_TO_OBJECT.items():
        if (obj_dict["obj_name"] == full_name or obj_dict["obj_description"] == full_name) and ord(
            obj_dict["obj_class"]
        ) == ItemClasses.WEAPON.value:
            break

    item = Item.from_inv(
        inv_letter="a",
        inv_str=np.array([ord(c) for c in full_name]),
        inv_oclass=ord(obj_dict["obj_class"]),
        inv_glyph=glyph,
    )
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
    for glyph, obj_dict in GLYPH_TO_OBJECT.items():
        if (obj_dict["obj_name"] == full_name or obj_dict["obj_description"] == full_name) and ord(
            obj_dict["obj_class"]
        ) == ItemClasses.WEAPON.value:
            break

    item = Item.from_inv(
        inv_letter="a",
        inv_str=np.array([ord(c) for c in full_name]),
        inv_oclass=ord(obj_dict["obj_class"]),
        inv_glyph=glyph,
    )
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
    for glyph, obj_dict in GLYPH_TO_OBJECT.items():
        if obj_dict["obj_name"] == full_name and obj_dict["obj_class"] == chr(ItemClasses.ARMOR.value):
            break
    obj = obj_dict["obj"]
    bonus = arm_bonus(obj, enchantment, erosion)

    assert obj.a_ac == base_ac
    assert bonus == expected_bonus


@pytest.mark.parametrize(
    "full_name,enchantment",
    [
        ("battle-axe", None),
        ("+2 battle-axe", 2),
        ("-1 battle-axe", -1),
        ("a +1 dagger", 1),
        ("51 +2 crossbow bolts (in quiver pouch)", 2),
        ("37 blessed +0 crossbow bolts", 0),
        ("an uncursed +2 cloak of displacement (being worn)", 2),
    ],
)
def test_enchantment(full_name, enchantment):
    assert ItemEnchantment.from_name(full_name).value == enchantment

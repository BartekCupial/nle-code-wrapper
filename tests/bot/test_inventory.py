import numpy as np
import pytest
from nle import nethack
from nle_utils.item import ItemClasses, ItemEnchantment, ItemErosion

from nle_code_wrapper.bot.inventory import GLYPH_TO_OBJECT, Item


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
    "name",
    [
        "arrow",
        "elven arrow",
        "orcish arrow",
        "silver arrow",
        "ya",
        "crossbow bolt",
    ],
)
def test_item_firing_projectiles(name):
    for glyph, glyph_object in GLYPH_TO_OBJECT.items():
        if glyph_object.name == name:
            break

    item = Item(
        inv_letter="a",
        inv_str=np.array([ord(c) for c in name], dtype=np.uint8),
        inv_oclass=ItemClasses.WEAPON.value,
        inv_glyph=glyph,
    )
    assert item.is_firing_projectile


@pytest.mark.parametrize(
    "name",
    [
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
    ],
)
def test_item_thrown_projectiles(name):
    for glyph, glyph_object in GLYPH_TO_OBJECT.items():
        if glyph_object.name == name:
            break

    item = Item(
        inv_letter="a",
        inv_str=np.array([ord(c) for c in name], dtype=np.uint8),
        inv_oclass=ItemClasses.WEAPON.value,
        inv_glyph=glyph,
    )
    assert item.is_thrown_projectile


@pytest.mark.parametrize(
    "name,base_ac,enchantment,erosion,expected_bonus",
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
def test_arm_bonus(name, base_ac, enchantment, erosion, expected_bonus):
    for glyph, glyph_object in GLYPH_TO_OBJECT.items():
        if glyph_object.name == name:
            break
    else:
        glyph = None

    item = Item(
        inv_letter="a",
        inv_str=np.array([ord(c) for c in name], dtype=np.uint8),
        inv_oclass=ItemClasses.WEAPON.value,
        inv_glyph=glyph,
    )
    item.enchantment = ItemEnchantment(enchantment)
    item.erosion = ItemErosion(erosion)

    assert item.object.a_ac == base_ac
    assert item.arm_bonus() == expected_bonus


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


@pytest.mark.parametrize(
    "name,nutrition",
    [
        # /* special case because it's not mergable */
        ("meat ring", 5),
        # /* corpses */
        ("lichen corpse", 200),
        ("lizard corpse", 40),
        ("mastodon corpse", 800),
        ("killer bee corpse", 5),
        ("glob of gray ooze", 20),
        # /* meat */
        ("tripe ration", 200),
        ("corpse", 0),
        ("egg", 80),
        ("meatball", 5),
        ("meat stick", 5),
        ("huge chunk of meat", 2000),
        # /* fruits & veggies */
        ("kelp frond", 30),
        ("eucalyptus leaf", 30),
        ("apple", 50),
        ("orange", 80),
        ("pear", 50),
        ("melon", 100),
        ("banana", 80),
        ("carrot", 50),
        ("sprig of wolfsbane", 40),
        ("clove of garlic", 40),
        ("slime mold", 250),
        # /* people food */
        ("lump of royal jelly", 200),
        ("cream pie", 100),
        ("candy bar", 100),
        ("fortune cookie", 40),
        ("pancake", 200),
        ("lembas wafer", 800),
        ("cram ration", 600),
        ("food ration", 800),
        ("K-ration", 400),
        ("C-ration", 300),
        # /* tins have type specified by obj->spe (+1 for spinach, other implies
        #    flesh; negative specifies preparation method {homemade,boiled,&c})
        #    and by obj->corpsenm (type of monster flesh) */
        ("tin", 0),
    ],
)
def test_nutrition(name, nutrition):
    for glyph, glyph_object in GLYPH_TO_OBJECT.items():
        if glyph_object.name == name:
            break
    else:
        glyph = None

    item = Item(
        inv_letter="a",
        inv_str=np.array([ord(c) for c in name], dtype=np.uint8),
        inv_oclass=ItemClasses.COMESTIBLES.value,
        inv_glyph=glyph,
    )

    assert item.nutrition == nutrition


@pytest.mark.parametrize(
    "full_name,name,oclass,weight",
    [
        ("100 gold pieces", "gold piece", ItemClasses.COIN, 1),
        ("red gem", "ruby", ItemClasses.GEM, 1),
        ("shiny ring", "ring of gain strength", ItemClasses.RING, 3),
        ("scroll labeled MAPIRO MAHAMA DIROMAT", "scroll of enchant armor", ItemClasses.SCROLL, 5),
        ("long wand", "wand of wishing", ItemClasses.WAND, 7),
        ("luckstone", "luckstone", ItemClasses.GEM, 10),
        ("tripe ration", "tripe ration", ItemClasses.COMESTIBLES, 10),
        ("lizard corpse", "lizard corpse", ItemClasses.COMESTIBLES, 10),
        ("bugle", "bugle", ItemClasses.TOOL, 10),
        ("looking glass", "mirror", ItemClasses.TOOL, 13),
        ("flail", "flail", ItemClasses.WEAPON, 15),
        ("bag", "bag of holding", ItemClasses.TOOL, 15),
        ("oval amulet", "amulet of life saving", ItemClasses.AMULET, 20),
        ("dark green potion", "potion of speed", ItemClasses.POTION, 20),
        ("food ration", "food ration", ItemClasses.COMESTIBLES, 20),
        ("lichen corpse", "lichen corpse", ItemClasses.COMESTIBLES, 20),
        ("unicorn horn", "unicorn horn", ItemClasses.TOOL, 20),
        ("mace", "mace", ItemClasses.WEAPON, 30),
        ("gray dragon scale mail", "gray dragon scale mail", ItemClasses.ARMOR, 40),
        ("long sword", "long sword", ItemClasses.WEAPON, 40),
        ("pink spellbook", "spellbook of sleep", ItemClasses.SPELLBOOK, 50),
        ("fauchard", "fauchard", ItemClasses.WEAPON, 60),
        ("pick-axe", "pick-axe", ItemClasses.TOOL, 100),
        ("plate mail", "plate mail", ItemClasses.ARMOR, 450),
        ("iron ball", "heavy iron ball", ItemClasses.RANDOM, 480),
        ("loadstone", "loadstone", ItemClasses.ROCK, 500),
        ("human corpse", "human corpse", ItemClasses.COMESTIBLES, 1450),
        ("blue dragon corpse", "blue dragon corpse", ItemClasses.COMESTIBLES, 4500),
        ("boulder", "boulder", ItemClasses.RANDOM, 6000),
    ],
)
def test_weight(full_name, name, oclass, weight):
    for glyph, glyph_object in GLYPH_TO_OBJECT.items():
        if glyph_object.name == name:
            break
    else:
        assert False

    item = Item(
        inv_letter="a",
        inv_str=np.array([ord(c) for c in full_name], dtype=np.uint8),
        inv_oclass=oclass.value,
        inv_glyph=glyph,
    )

    assert item.weight == weight

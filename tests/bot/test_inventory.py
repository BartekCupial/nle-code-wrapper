import pytest

from nle_code_wrapper.bot.inventory import Item, ItemDatabase, ItemParser


@pytest.fixture
def item_parser():
    return ItemParser()


@pytest.fixture
def item_database():
    return ItemDatabase()


@pytest.fixture
def get_item(item_parser, item_database):
    def _get_item(text):
        properties = item_parser(text)
        if properties["item_category"] is None:
            properties["item_category"] = item_database[properties["name"]].item_category

        item = Item(
            text=text,
            item_class=item_database.get(properties["name"]),
            **properties,
        )
        return item

    return _get_item


@pytest.mark.parametrize(
    "text,expected",
    [
        ("a rusty small shield", 1),
        ("a very rusty corroded small shield", 2),
        ("a thoroughly burnt very corroded small shield", 3),
        ("a rusty rotted small shield", 1),
        ("a very rusty thoroughly corroded small shield", 3),
        ("a thoroughly burnt very corroded rusty small shield", 3),
    ],
)
def test_greatest_erosion(get_item, text, expected):
    item = get_item(text)
    assert item.erosion.value == expected


@pytest.mark.parametrize(
    "text",
    [
        "an arrow",
        "an elven arrow",
        "an orcish arrow",
        "a silver arrow",
        "a ya",
        "a crossbow bolt",
    ],
)
def test_item_firing_projectiles(get_item, text):
    item = get_item(text)
    assert item.is_firing_projectile


@pytest.mark.parametrize(
    "text",
    [
        "a boomerang",
        "a dagger",
        "a elven dagger",
        "a orcish dagger",
        "a silver dagger",
        "a worm tooth",
        "a crysknife",
        "a knife",
        "a athame",
        "a scalpel",
        "a stiletto",
        "a dart",
        "a shuriken",
    ],
)
def test_item_thrown_projectiles(get_item, text):
    item = get_item(text)
    assert item.is_thrown_projectile


@pytest.mark.parametrize(
    "text,base_ac,expected_bonus",
    [
        # # Basic cases - no erosion
        ("a leather armor", 2, 2),  # Base AC only
        ("a +1 leather armor", 2, 3),  # Base AC + enchantment
        # # # Erosion cases
        ("a rotted leather armor", 2, 1),  # Partial erosion
        ("a rusty corroded helmet", 1, 0),  # Full erosion
        ("a thoroughly burnt helmet", 1, 0),  # Over-erosion (should cap at AC)
        # Enchantment + erosion combinations
        ("a rotted +2 leather armor", 2, 3),  # +2 enchant, 1 erosion
        ("a rusty -1 plate mail", 7, 5),  # Negative enchant, partial erosion
        ("a thoroughly corroded +3 plate mail", 7, 7),  # High enchant, high erosion
        # Different armor types
        ("a crystal plate mail", 7, 7),  # High AC armor
        ("a Hawaiian shirt", 0, 0),  # Low AC armor
    ],
)
def test_arm_bonus(get_item, text, base_ac, expected_bonus):
    item = get_item(text)
    assert item.object.a_ac == base_ac
    assert item.arm_bonus == expected_bonus


@pytest.mark.parametrize(
    "text,enchantment",
    [
        ("a battle-axe", 0),
        ("a +2 battle-axe", 2),
        ("a -1 battle-axe", -1),
        ("a +1 dagger", 1),
        ("51 +2 crossbow bolts (in quiver pouch)", 2),
        ("37 blessed +0 crossbow bolts", 0),
        ("an uncursed +2 cloak of displacement (being worn)", 2),
    ],
)
def test_enchantment(get_item, text, enchantment):
    item = get_item(text)
    assert item.enchantment.value == enchantment


@pytest.mark.parametrize(
    "text,nutrition",
    [
        # /* special case because it's not mergable */
        ("a meat ring", 5),
        # # /* corpses */
        ("a lichen corpse", 200),
        ("2 lizard corpses", 80),
        ("a mastodon corpse", 800),
        ("a killer bee corpse", 5),
        ("a glob of gray ooze", 20),
        # /* meat */
        ("a tripe ration", 200),
        ("a newt corpse", 20),
        ("an egg", 80),
        ("a meatball", 5),
        ("a meat stick", 5),
        ("a huge chunk of meat", 2000),
        # /* fruits & veggies */
        ("a kelp frond", 30),
        ("a eucalyptus leaf", 30),
        ("a apple", 50),
        ("a orange", 80),
        ("a pear", 50),
        ("a melon", 100),
        ("a banana", 80),
        ("a carrot", 50),
        ("a sprig of wolfsbane", 40),
        ("a clove of garlic", 40),
        ("a slime mold", 250),
        # /* people food */
        ("a lump of royal jelly", 200),
        ("a cream pie", 100),
        ("a candy bar", 100),
        ("a fortune cookie", 40),
        ("a pancake", 200),
        ("a lembas wafer", 800),
        ("a cram ration", 600),
        ("a food ration", 800),
        ("a K-ration", 400),
        ("a C-ration", 300),
        # /* tins have type specified by obj->spe (+1 for spinach, other implies
        #    flesh; negative specifies preparation method {homemade,boiled,&c})
        #    and by obj->corpsenm (type of monster flesh) */
        ("a tin", 0),
    ],
)
def test_nutrition(get_item, text, nutrition):
    item = get_item(text)
    assert item.nutrition == nutrition


@pytest.mark.parametrize(
    "text,weight",
    [
        ("100 gold pieces", 1),
        ("a red gem", 1),
        ("a shiny ring", 3),
        ("a scroll labeled MAPIRO MAHAMA DIROMAT", 5),
        ("a long wand", 7),
        ("a luckstone", 10),
        ("a tripe ration", 10),
        ("a lizard corpse", 10),
        ("a bugle", 10),
        ("a looking glass", 13),
        ("a flail", 15),
        ("a bag", 15),
        ("an oval amulet", 20),
        ("a dark green potion", 20),
        ("a food ration", 20),
        ("a lichen corpse", 20),
        ("an unicorn horn", 20),
        ("a mace", 30),
        ("a gray dragon scale mail", 40),
        ("a long sword", 40),
        ("a pink spellbook", 50),
        ("a fauchard", 60),
        ("a pick-axe", 100),
        ("a plate mail", 450),
        ("a heavy iron ball", 480),
        ("a loadstone", 500),
        ("a human corpse", 1450),
        ("a blue dragon corpse", 4500),
        ("a boulder", 6000),
    ],
)
def test_weight(get_item, text, weight):
    item = get_item(text)
    assert item.weight == weight


@pytest.mark.parametrize(
    "text",
    [
        "a wakizashi",
        "a ninja-to",
        "a nunchaku",
        "a shito",
        "a naginata",
        "a gunyoki",
        "a osaku",
        "a tanko",
        "a kabuto",
        "a yugake",
        "an unlabeled scroll",
        "5 unlabeled scrolls",
        "a scroll of blank paper",
        "a flint stone",
        "2 flint stones",
        "a pair of lenses",
        "11 knives",
        "4 eucalyptus leaves",
    ],
)
def test_special(get_item, text):
    get_item(text)


@pytest.mark.parametrize(
    "text",
    [
        "an Excalibur",
        "a Stormbringer",
        "a Mjollnir",
        "a Cleaver",
        "a Grimtooth",
        "a Orcrist",
        "a Sting",
        "a Magicbane",
        "a Frost Brand",
        "a Fire Brand",
        "a Dragonbane",
        "a Demonbane",
        "a Werebane",
        "a Grayswandir",
        "a Giantslayer",
        "a Ogresmasher",
        "a Trollsbane",
        "a Vorpal Blade",
        "a Snickersnee",
        "a Sunsword",
        "a glass orb named The Orb of Detection",
        "a gray stone named The Heart of Ahriman",
        "a mace named The Sceptre of Might",
        "a crystal ball named The Palantir of Westernesse",
        "a quarterstaff named The Staff of Aesculapius",
        "a mirror named The Magic Mirror of Merlin",
        "a pair of lenses named The Eyes of the Overworld",
        "a helmet named The Mitre of Holiness",
        "a bow named The Longbow of Diana",
        "a key named The Master Key of Thievery",
        "a tsurugi named The Tsurugi of Muramasa",
        "a credit card named The Platinum Yendorian Express Card",
        "a glass orb named The Orb of Fate",
        "a amulet of ESP named The Eye of the Aethiopica",
    ],
)
def test_artifacts(get_item, text):
    get_item(text)

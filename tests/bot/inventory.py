import numpy as np
import pytest
from nle import nethack
from nle_utils.item import ItemClasses

from nle_code_wrapper.bot.inventory import OBJECT_NAMES, Inventory, Item, get_object


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
    assert item.is_firing_projectile()


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
    assert item.is_thrown_projectile()

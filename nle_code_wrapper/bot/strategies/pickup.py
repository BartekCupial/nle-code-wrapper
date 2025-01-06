from functools import wraps
from types import FunctionType
from typing import Callable

from nle.nethack import actions as A
from nle_utils.glyph import G
from nle_utils.item import ArmorType, ItemClasses

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import GLYPH_TO_OBJECT
from nle_code_wrapper.bot.strategies.goto import goto_glyph
from nle_code_wrapper.bot.strategy import strategy


@strategy
def pickup_item(bot: "Bot", item=G.ITEMS):
    if goto_glyph(bot, item):
        bot.step(A.Command.PICKUP)
        return True
    else:
        return False


# PICKUP ITEM CLASS


def create_item_pickup_function(item_class: ItemClasses) -> Callable[["Bot"], bool]:
    """Dynamically create a function that picks up a given item class type."""

    def pickup_func(bot: "Bot"):
        return pickup_item(bot, getattr(G, f"{item_class.name}_CLASS"))

    pickup_func.__name__ = f"pickup_{item_class.name.lower()}"
    pickup_func.__doc__ = f"Picks up {item_class.name.lower()} from the ground."
    return pickup_func


def pickup_coins(bot: "Bot") -> bool:
    ...


def pickup_amulet(bot: "Bot") -> bool:
    ...


def pickup_weapon(bot: "Bot") -> bool:
    ...


def pickup_armor(bot: "Bot") -> bool:
    ...


def pickup_compestibles(bot: "Bot") -> bool:
    ...


def pickup_scross(bot: "Bot") -> bool:
    ...


def pickup_spellbook(bot: "Bot") -> bool:
    ...


def pickup_potion(bot: "Bot") -> bool:
    ...


def pickup_ring(bot: "Bot") -> bool:
    ...


def pickup_wand(bot: "Bot") -> bool:
    ...


def pickup_tool(bot: "Bot") -> bool:
    ...


def pickup_gem(bot: "Bot") -> bool:
    ...


def pickup_rocks(bot: "Bot") -> bool:
    ...


def pickup_ball(bot: "Bot") -> bool:
    ...


for item_class in ItemClasses:
    func_name = f"pickup_{item_class.name.lower()}"
    globals()[func_name] = create_item_pickup_function(item_class)


# PICKUP ARMOR


def pickup_suit(bot: "Bot") -> bool:
    ...


def pickup_shield(bot: "Bot") -> bool:
    ...


def pickup_helm(bot: "Bot") -> bool:
    ...


def pickup_boots(bot: "Bot") -> bool:
    ...


def pickup_gloves(bot: "Bot") -> bool:
    ...


def pickup_cloak(bot: "Bot") -> bool:
    ...


def pickup_shirt(bot: "Bot") -> bool:
    ...


def create_armor_pickup_function(armor_class: ArmorType) -> Callable[["Bot"], bool]:
    """Dynamically create a function that picks up a given armor type."""

    def pickup_func(bot: "Bot", a_type=armor_class) -> bool:
        armor_glyphs = frozenset(
            glyph
            for glyph, obj in GLYPH_TO_OBJECT.items()
            if obj["obj_class"] == chr(ItemClasses.ARMOR.value) and obj["obj"].oc_armcat == a_type.value
        )
        return pickup_item(bot, armor_glyphs)

    pickup_func.__name__ = f"pickup_{armor_class.name.lower()}"
    pickup_func.__doc__ = f"Picks up {armor_class.name.lower()} from the ground."
    return pickup_func


for armor_class in ArmorType:
    func_name = f"pickup_{armor_class.name.lower()}"
    globals()[func_name] = create_armor_pickup_function(armor_class)


# PICKUP TOOLS


def create_tool_pickup_function(description: str, name: str) -> Callable[["Bot"], bool]:
    """
    Creates a pickup function for specific tools

    Args:
        description (str): The tool description to match
        name (str): Name of the tool type for the function name

    Returns:
        function: A pickup function for the specified tool
    """

    def pickup_tool(bot: "Bot"):
        tool_glyphs = frozenset(
            glyph
            for glyph, obj in GLYPH_TO_OBJECT.items()
            if obj["obj_class"] == chr(ItemClasses.TOOL.value) and obj["obj_description"] == description
        )
        return pickup_item(bot, tool_glyphs)

    pickup_tool.__name__ = f"pickup_{name}"
    return pickup_tool


def pickup_horn(bot: "Bot") -> bool:
    ...


pickup_horn = create_tool_pickup_function("horn", "horn")

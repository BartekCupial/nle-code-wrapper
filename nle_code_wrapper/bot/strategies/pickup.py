import re
from typing import Callable

from nle.nethack import actions as A
from nle_utils.glyph import G
from nle_utils.item import ArmorType, ItemClasses

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import GLYPH_TO_OBJECT
from nle_code_wrapper.bot.strategies.goto import goto_glyph
from nle_code_wrapper.bot.strategy import strategy


@strategy
def pickup_item(bot: "Bot", item_class: ItemClasses):
    item_glyphs = getattr(G, f"{item_class.name}_CLASS")

    if goto_glyph(bot, item_glyphs):
        bot.step(A.Command.PICKUP)

        if bot.xwaitingforspace:
            lines = bot.popup_message.split("\n")
            mark_items = False
            for line in lines:
                if mark_items:
                    if re.match("[a-zA-Z] -", line):  # example: e - a cloudy potion
                        # mark item for picking up
                        bot.type_text(line[0])  # first character in line is an item letter
                    else:
                        break

                # when we reach item category we are interested in
                if line.lower() == item_class.name.lower():
                    mark_items = True

            if mark_items:  # confirm only if we reached desired category
                bot.step(A.MiscAction.MORE)  # confirm

        return True
    else:
        return False


@strategy
def pickup_glyph(bot: "Bot", item_glyph):
    if goto_glyph(bot, item_glyph):
        bot.step(A.Command.PICKUP)
        return True
    else:
        return False


# PICKUP ITEM CLASS


def create_item_pickup_function(item_class: ItemClasses) -> Callable[["Bot"], bool]:
    """Dynamically create a function that picks up a given item class type."""

    def pickup_func(bot: "Bot"):
        return pickup_item(bot, item_class)

    pickup_func.__name__ = f"pickup_{item_class.name.lower()}"
    pickup_func.__doc__ = f"Picks up {item_class.name.lower()} from the ground."
    return pickup_func


def pickup_coin(bot: "Bot") -> bool:
    ...


def pickup_amulet(bot: "Bot") -> bool:
    ...


def pickup_weapon(bot: "Bot") -> bool:
    ...


def pickup_armor(bot: "Bot") -> bool:
    ...


def pickup_compestibles(bot: "Bot") -> bool:
    ...


def pickup_scroll(bot: "Bot") -> bool:
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


def pickup_rock(bot: "Bot") -> bool:
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

    def pickup_func(bot: "Bot") -> bool:
        armor_glyphs = frozenset(
            glyph
            for glyph, obj in GLYPH_TO_OBJECT.items()
            if obj["obj_class"] == chr(ItemClasses.ARMOR.value) and obj["obj"].oc_armcat == armor_class.value
        )
        return pickup_glyph(bot, armor_glyphs)

    pickup_func.__name__ = f"pickup_{armor_class.name.lower()}"
    pickup_func.__doc__ = f"Picks up {armor_class.name.lower()} from the ground."
    return pickup_func


for armor_class in ArmorType:
    func_name = f"pickup_{armor_class.name.lower()}"
    globals()[func_name] = create_armor_pickup_function(armor_class)


# PICKUP TOOLS


# def create_tool_pickup_function(description: str, name: str) -> Callable[["Bot"], bool]:
#     """
#     Creates a pickup function for specific tools

#     Args:
#         description (str): The tool description to match
#         name (str): Name of the tool type for the function name

#     Returns:
#         function: A pickup function for the specified tool
#     """

#     def pickup_tool(bot: "Bot"):
#         tool_glyphs = frozenset(
#             glyph
#             for glyph, obj in GLYPH_TO_OBJECT.items()
#             if obj["obj_class"] == chr(ItemClasses.TOOL.value) and obj["obj_description"] == description
#         )
#         return pickup_glyph(bot, tool_glyphs)

#     pickup_tool.__name__ = f"pickup_{name}"
#     return pickup_tool


# def pickup_horn(bot: "Bot") -> bool:
#     ...


# pickup_horn = create_tool_pickup_function("horn", "horn")

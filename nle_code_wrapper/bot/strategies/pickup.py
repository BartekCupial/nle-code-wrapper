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
    bot.step(A.Command.PICKUP)

    # Check if the game shows a single item, e.g. "a - a cloudy potion"
    if re.match(r"[a-zA-Z]\s-\s", bot.message):
        # If there's exactly one item below us, just select its letter.
        letter = bot.message[0]
        bot.type_text(letter)
        succ = True

    # Check if there's a pile or multiple items
    elif (
        "There are several objects here" in bot.message or "Pick up what?" in bot.message or "items here" in bot.message
    ):
        # For a pile, just mark success and let the code below handle
        succ = True

    else:
        # No obvious item under us; try moving to an appropriate glyph
        item_glyphs = getattr(G, f"{item_class.name}_CLASS")

        succ = False
        if goto_glyph(bot, item_glyphs):
            succ = True
            bot.step(A.Command.PICKUP)

        # If we can't find the specific item glyph, try all items
        # TODO: we could pickup single item based on message,
        # it would require mapping message to item class
        # for now easier to drop the item if it has wrong class
        elif goto_glyph(bot, G.ITEMS):
            succ = True
            bot.step(A.Command.PICKUP)

        # Finally, try corpses if applicable
        # TODO: implement loot corpses strategy?
        # TODO: also eat corpses
        elif goto_glyph(bot, G.CORPSES):
            succ = True
            bot.step(A.Command.PICKUP)

        item_glyphs = getattr(G, f"{item_class.name}_CLASS")

    # If we succeeded in initiating a pickup (single item, pile, or walking onto it):
    if succ:
        if bot.xwaitingforspace:
            lines = bot.popup_message.split("\n")
            mark_items = False
            while lines:
                line = lines.pop(0)

                # 0) if we reach (end) get out
                if "(end)" in line:
                    bot.step(A.MiscAction.MORE)

                # 1) when we reach item category we are interested in start marking
                if line.lower().startswith(item_class.name.lower()):
                    mark_items = True
                    continue

                # 2) if we ehxausted the current page go to the next one
                if re.match("\(\d+ of \d+\)", line):  # NOQA: W605
                    bot.type_text(" ")
                    lines = bot.popup_message.split("\n")
                    continue

                # 3) mark items for picking up
                if mark_items:
                    # example: e - a cloudy potion
                    if re.match("[a-zA-Z] -", line):
                        # first character in line is an item letter
                        bot.type_text(line[0])
                    else:
                        if line != "":
                            bot.step(A.MiscAction.MORE)  # confirm
                        return True
        else:
            letter = bot.message[0]
            for item in bot.inventory.items:
                if item.letter == ord(letter):
                    if item.item_class == item_class:
                        return True
                    else:
                        bot.step(A.Command.DROP)
                        bot.type_text(letter)

    return False


@strategy
def pickup_glyph(bot: "Bot", item_glyph):
    if goto_glyph(bot, item_glyph):
        bot.step(A.Command.PICKUP)
        return True
    else:
        return False


# PICKUP ITEM CLASS


def pickup_coin(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.COIN)


def pickup_amulet(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.AMULET)


def pickup_weapon(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.WEAPON)


def pickup_armor(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.ARMOR)


def pickup_compestibles(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.COMPESTIBLES)


def pickup_scroll(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.SCROLL)


def pickup_spellbook(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.SPELLBOOK)


def pickup_potion(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.POTION)


def pickup_ring(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.RING)


def pickup_wand(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.WAND)


def pickup_tool(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.TOOL)


def pickup_gem(bot: "Bot") -> bool:
    return pickup_item(bot, ItemClasses.GEM)


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

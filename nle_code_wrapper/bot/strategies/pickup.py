import re

from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import Item, ItemClass
from nle_code_wrapper.bot.strategies.goto import goto_glyph
from nle_code_wrapper.bot.strategy import strategy


def pickup_multipage(bot: "Bot", item_class: ItemClass, text: str):
    # Pattern for items
    item_pattern = r"([a-zA-Z]) - (.+)"

    # Pattern for end markers
    end_pattern = r"\(end\)"
    page_pattern = r"\((\d+) of \1\)"  # Same number (e.g., "2 of 2")
    diff_page_pattern = r"\((\d+) of (\d+)\)"  # Different numbers (e.g., "1 of 2")

    items = re.finditer(item_pattern, text, re.MULTILINE)
    for match in items:
        letter, item = match.group(1), match.group(2)
        item = Item.from_text(item)
        if item.item_class == item_class:
            bot.type_text(letter)

    # Check for (end)
    if re.search(end_pattern, text):
        bot.step(A.MiscAction.MORE)

    # Check for (n of n) - same number
    elif re.search(page_pattern, text):
        bot.step(A.MiscAction.MORE)

    # Check for (n of m) - different numbers
    elif re.search(diff_page_pattern, text):
        bot.step(A.TextCharacters.SPACE)
        pickup_multipage(bot, item_class, bot.message)


def look(bot: "Bot", item_class: ItemClass) -> bool:
    # look below us
    bot.step(A.Command.LOOK)

    # only one item
    if match := re.search(r"You see here(.*?)\.", bot.message):
        text = match.group(1).strip()
        item = Item.from_text(text)
        if item.item_class == item_class:
            bot.step(A.Command.PICKUP)
            return True

    # multiple items
    elif "Things that are here:" in bot.message:
        items = []
        lines = bot.message.strip().split("\n")
        for line in lines[1:]:
            item = Item.from_text(line)
            items.append(item)

        # check if there is an item we would like to pick up
        if any([item.item_class == item_class for item in items]):
            bot.step(A.Command.PICKUP)
            pickup_multipage(bot, item_class, bot.message)
            return True

    return False


@strategy
def pickup_item(bot: "Bot", item_class: ItemClass):
    if look(bot, item_class):
        return True

    if goto_glyph(bot, G.ITEMS.union(G.CORPSES)):
        if look(bot, item_class):
            return True

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
    """
    Makes bot pick up coins from the floor.
    """
    return pickup_item(bot, ItemClass.COIN)


def pickup_amulet(bot: "Bot") -> bool:
    """
    Makes bot pick up amulets from the floor.
    """
    return pickup_item(bot, ItemClass.AMULET)


def pickup_weapon(bot: "Bot") -> bool:
    """
    Makes bot pick up weapons from the floor.
    """
    return pickup_item(bot, ItemClass.WEAPON)


def pickup_armor(bot: "Bot") -> bool:
    """
    Makes bot pick up armor and shieds from the floor.
    """
    return pickup_item(bot, ItemClass.ARMOR)


def pickup_food(bot: "Bot") -> bool:
    """
    Makes bot pick up food from the floor.
    """
    return pickup_item(bot, ItemClass.COMESTIBLES)


@strategy
def pickup_corpse(bot: "Bot") -> bool:
    """
    Makes bot pick up corpse from the floor.
    """
    return pickup_item(bot, ItemClass.CORPSE)


def pickup_scroll(bot: "Bot") -> bool:
    """
    Makes bot pick up scrolls from the floor.
    """
    return pickup_item(bot, ItemClass.SCROLL)


def pickup_spellbook(bot: "Bot") -> bool:
    """
    Makes bot pick up spellbooks from the floor.
    """
    return pickup_item(bot, ItemClass.SPELLBOOK)


def pickup_potion(bot: "Bot") -> bool:
    """
    Makes bot pick up potions from the floor.
    """
    return pickup_item(bot, ItemClass.POTION)


def pickup_ring(bot: "Bot") -> bool:
    """
    Makes bot pick up rings from the floor.
    """
    return pickup_item(bot, ItemClass.RING)


def pickup_wand(bot: "Bot") -> bool:
    """
    Makes bot pick up wands from the floor.
    """
    return pickup_item(bot, ItemClass.WAND)


def pickup_tool(bot: "Bot") -> bool:
    """
    Makes bot pick up tools from the floor.
    """
    return pickup_item(bot, ItemClass.TOOL)


def pickup_gem(bot: "Bot") -> bool:
    """
    Makes bot pick up gems from the floor.
    """
    return pickup_item(bot, ItemClass.GEM)


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
#             if obj["obj_class"] == chr(ItemClass.TOOL.value) and obj["obj_description"] == description
#         )
#         return pickup_glyph(bot, tool_glyphs)

#     pickup_tool.__name__ = f"pickup_{name}"
#     return pickup_tool


# def pickup_horn(bot: "Bot") -> bool:
#     ...


# pickup_horn = create_tool_pickup_function("horn", "horn")

import re
from typing import Callable, List, Optional

from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import ArmorClass, Item, ItemBeatitude, ItemCategory
from nle_code_wrapper.bot.strategies.goto import goto_glyph
from nle_code_wrapper.bot.strategy import strategy


def select_drop_category(bot: "Bot", what: str):
    """Selects item category to drop from inventory"""
    bot.step(A.Command.DROPTYPE)

    pattern = r"([$a-zA-Z]) - (.+)"
    lines = re.finditer(pattern, bot.message, re.MULTILINE)
    for match in lines:
        letter = match.group(1)
        name = match.group(2)

        if name.lower() == what:
            bot.type_text(letter)
            bot.step(A.MiscAction.MORE)

            return True

    return False


def drop_items(bot: "Bot", category: str, condition: Callable) -> bool:
    """
    Generic helper for dropping items.
    - category: inventory category (str, e.g. "armor", "potions")
    - condition: function (Item -> bool) that determines whether to drop the item
    """
    if not select_drop_category(bot, category):
        return False

    was_any = False
    for item in bot.inventory[category]:
        if condition(item):
            bot.step(item.letter)
            was_any = True

    bot.step(A.TextCharacters.SPACE)
    return was_any


@strategy
def drop_unequipped_armor(bot: "Bot") -> bool:
    """Drops all unequipped armor from inventory."""
    return drop_items(bot, "armor", lambda item: not item.equipped)


@strategy
def drop_unequipped_weapons(bot: "Bot") -> bool:
    """Drops all unequipped weapons from inventory."""
    return drop_items(bot, "weapons", lambda item: not item.equipped)


@strategy
def drop_unidentified_scrolls(bot: "Bot") -> bool:
    """Drops all unidentified scrolls from inventory."""
    return drop_items(bot, "scrolls", lambda item: item.beatitude == ItemBeatitude.UNKNOWN)


@strategy
def drop_unidentified_potions(bot: "Bot") -> bool:
    """Drops all unidentified potions from inventory."""
    return drop_items(bot, "potions", lambda item: item.beatitude == ItemBeatitude.UNKNOWN)


@strategy
def drop_unidentified_spellbooks(bot: "Bot") -> bool:
    """Drops all unidentified spellbooks from inventory."""
    return drop_items(bot, "spellbooks", lambda item: item.beatitude == ItemBeatitude.UNKNOWN)


@strategy
def drop_unidentified_wands(bot: "Bot") -> bool:
    """Drops all unidentified wands from inventory."""
    return drop_items(bot, "wands", lambda item: item.beatitude == ItemBeatitude.UNKNOWN)


@strategy
def drop_unidentified_rings(bot: "Bot") -> bool:
    """Drops all unidentified rings from inventory."""
    return drop_items(bot, "rings", lambda item: item.beatitude == ItemBeatitude.UNKNOWN)


@strategy
def drop_unidentified_amulets(bot: "Bot") -> bool:
    """Drops all unidentified amulets from inventory."""
    return drop_items(bot, "amulets", lambda item: item.beatitude == ItemBeatitude.UNKNOWN)


@strategy
def drop_unidentified_food(bot: "Bot") -> bool:
    """Drops all unidentified food from inventory."""
    return drop_items(
        bot, "food", lambda item: item.beatitude == ItemBeatitude.UNKNOWN and item.category == ItemCategory.COMESTIBLES
    )


@strategy
def drop_corpses(bot: "Bot") -> bool:
    """Drops all corpses from inventory."""
    return drop_items(bot, "food", lambda item: item.category == ItemCategory.CORPSE)


@strategy
def drop_coins(bot: "Bot") -> bool:
    """Drops all coins from inventory."""
    return drop_items(bot, "coins", lambda item: True)


@strategy
def drop_cursed_items(bot: "Bot") -> bool:
    """Drops all cursed items from inventory."""
    if not select_drop_category(bot, "cursed"):
        return False

    bot.step(A.Command.PICKUP)
    bot.step(A.TextCharacters.SPACE)

    return True


@strategy
def identify_items_altar(bot: "Bot") -> bool:
    """Identifies the beatitude on items at an altar."""
    if not goto_glyph(bot, G.ALTAR):
        return False

    # Items of unknown Bless/Curse status
    if not select_drop_category(bot, "items of unknown"):
        return False

    # select and drop all items
    bot.step(A.Command.PICKUP)
    bot.step(A.TextCharacters.SPACE)

    # select and pickup all items
    bot.step(A.Command.PICKUP)
    bot.step(A.Command.PICKUP)
    bot.step(A.TextCharacters.SPACE)

    return True

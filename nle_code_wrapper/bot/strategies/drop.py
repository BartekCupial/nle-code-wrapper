import re
from typing import Callable, List, Optional

from nle.nethack import actions as A

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import ArmorClass, Item, ItemBeatitude, ItemCategory
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

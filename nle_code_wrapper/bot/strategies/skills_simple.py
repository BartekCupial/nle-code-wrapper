from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategies.goto import goto_glyph
from nle_code_wrapper.bot.strategy import strategy


@strategy
def quaff_potion(bot: "Bot"):
    """
    Drinks random unidentified potion from inventory.
    """
    # TODO: random and unidentified
    items = bot.inventory["potions"]
    for item in items:
        bot.step(A.Command.QUAFF)
        bot.step(item.letter)
        return True

    return False


@strategy
def zap_wand(bot: "Bot"):
    """
    Zaps random unidentified wand from inventory
    """
    # TODO: random and unidentified
    items = bot.inventory["wands"]
    for item in items:
        bot.step(A.Command.ZAP)
        bot.step(item.letter)
        return True

    return False


@strategy
def read_scroll(bot: "Bot"):
    """
    Reads random unidentified scroll from inventory
    """
    # TODO: random and unidentified
    items = bot.inventory["scrolls"]
    for item in items:
        bot.step(A.Command.READ)
        bot.step(item.letter)

        # handle special cases:
        # scroll of identification
        if "What would you like to identify first?" in bot.message:
            # Check for items that need identification in the inventory
            unidentified_items = [letter for letter, item in bot.inventory.items.items() if not item.is_identified]

            if unidentified_items:
                # Identify each unidentified item one by one
                for item_letter in unidentified_items:
                    bot.step(item_letter)
                bot.step(A.MiscAction.MORE)

            if bot.xwaitingforspace:
                # If all items are identified, select all
                bot.step(A.Command.PICKUP)
                bot.step(A.MiscAction.MORE)

        # scroll of teleporation (with teleport control)
        elif "want to be teleported?" in bot.message:
            # TODO:
            bot.step(A.Command.ESC)

        # blessed scroll of teleporation
        elif "Do you wish to teleport?" in bot.message:
            # TODO:
            bot.type_text("n")

        # blessed scroll of genocide
        elif "What class of monsters do you wish to genocide?" in bot.message:
            # liches, mind flayers, rust monsters / disenchanters, sea monsters
            dangerous_classes = ["L", "h", "R", ";"]
            for monster in dangerous_classes:
                # TODO: check if not genocided
                bot.type_text(monster)
                bot.step(A.MiscAction.MORE)
                if "Wiped out all" in bot.message:
                    return True

        # scroll of genocide
        elif "What monster do you want to genocide?" in bot.message:
            priority_monsters = ["master mind flayer", "mind flayer", "disenchanter", "rust monster"]
            for monster in priority_monsters:
                for letter in monster:
                    bot.type_text(letter)
                bot.step(A.MiscAction.MORE)
                if f"Wiped out all {monster}" in bot.message:
                    return True

        # scroll of charging
        elif "What do you want to charge?" in bot.message:
            # TODO: add magic marker to the list
            # TODO: track if item was charged (dont charge more then once)
            # TODO: track usages of wands, se we can prioritize worn items
            # First try wands of death, then cold, then any other wands
            wand_priorities = [
                lambda item: "wand of death" in item.name,
                lambda item: "wand of cold" in item.name,
                lambda item: "wand of striking" in item.name,
                lambda item: "wand of fire" in item.name,
                lambda item: "wand of lightning" in item.name,
                lambda item: "wand of sleep" in item.name,
                lambda item: True,
            ]

            for priority_check in wand_priorities:
                for item in bot.inventory["wands"]:
                    if priority_check(item):
                        bot.step(item.letter)
                        return True

        return True

    return False


@strategy
def pray_altar(bot: "Bot"):
    """Prays at an altar if it is available."""
    if goto_glyph(bot, G.ALTAR):
        bot.safely_pray()
        return True

    return False


@strategy
def quaff_sink(bot: "Bot"):
    """Quaffs from a sink if it is available."""
    if goto_glyph(bot, G.SINK):
        bot.step(A.Command.QUAFF)
        if "Drink from the sink? [yn] (n)" in bot.message:
            bot.type_text("y")
            return True
    return False


@strategy
def quaff_fountain(bot: "Bot"):
    """Quaffs from a fountain if it is available."""
    if goto_glyph(bot, G.FOUNTAIN):
        bot.step(A.Command.QUAFF)
        if "Drink from the fountain? [yn] (n)" in bot.message:
            bot.type_text("y")
            return True
    return False

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
        return True

    return False


@strategy
def pray_altar(bot: "Bot"):
    if goto_glyph(bot, G.ALTAR):
        bot.step(A.Command.PRAY)
        if "Are you sure you want to pray? [yn] (n)" in bot.message:
            bot.type_text("y")
            return True
    return False


@strategy
def quaff_sink(bot: "Bot"):
    if goto_glyph(bot, G.SINK):
        bot.step(A.Command.QUAFF)
        if "Drink from the sink? [yn] (n)" in bot.message:
            bot.type_text("y")
            return True
    return False


@strategy
def quaff_fouintain(bot: "Bot"):
    if goto_glyph(bot, G.FOUNTAIN):
        bot.step(A.Command.QUAFF)
        if "Drink from the fountain? [yn] (n)" in bot.message:
            bot.type_text("y")
            return True
    return False

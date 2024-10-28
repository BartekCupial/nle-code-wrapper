from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategy import State, Strategy


@Strategy.wrap
def quaff_potion_from_inv(bot: "Bot"):
    inv_glyphs = bot.inv_glyphs
    inv_letters = bot.inv_letters

    # find the last potion in the inventory
    potion_char = None
    for char, glyph in zip(inv_letters, inv_glyphs):
        if glyph in G.POTION_CLASS:
            potion_char = char

    if potion_char is None:
        yield False
    else:
        bot.step(A.Command.QUAFF)
        bot.step(potion_char)
        yield True
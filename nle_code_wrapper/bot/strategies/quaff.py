from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot.bot import Bot


def quaff_potion_from_inv(bot: "Bot") -> bool:
    """
    Quaff a potion from the inventory.

    Args:
        bot (Bot): The bot object.

    Returns:
        bool: True if a potion was quaffed, False otherwise.
    """
    inv_glyphs = bot.inv_glyphs
    inv_letters = bot.inv_letters

    # find the last potion in the inventory
    potion_char = None
    for char, glyph in zip(inv_letters, inv_glyphs):
        if glyph in G.POTION_CLASS:
            potion_char = char

    if potion_char is None:
        return False
    else:
        bot.step(A.Command.QUAFF)
        bot.step(potion_char)
        return True

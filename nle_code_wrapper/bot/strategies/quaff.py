from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def quaff_potion_from_inv(bot: "Bot") -> bool:
    """
    Quaff a potion from the inventory.
    """
    potions = bot.inventory["potions"]

    if potions:
        # find the last potion in the inventory
        potion_char = potions[-1].letter
        bot.step(A.Command.QUAFF)
        bot.step(potion_char)
        return True
    else:
        return False

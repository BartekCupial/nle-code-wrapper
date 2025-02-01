from nle.nethack import actions as A

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def quaff_potion(bot: "Bot"):
    """
    Drinks potion from inventory.
    """
    items = bot.inventory["potions"]
    for item in items:
        bot.step(A.Command.QUAFF)
        bot.step(item.letter)
        return True

    return False

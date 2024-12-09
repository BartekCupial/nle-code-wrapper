from nle.nethack import actions as A

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def wear_boots(bot: "Bot"):
    items = bot.inventory["armor"]
    for item in items:
        if item.object.oc_armcat == 4:  # category for boots
            bot.step(A.Command.WEAR)
            bot.step(item.letter)
            return True

    return False


@strategy
def puton_ring(bot: "Bot"):
    items = bot.inventory["rings"]
    for item in items:
        bot.step(A.Command.PUTON)
        bot.step(item.letter)
        if "Which ring-finger, Right or Left?" in bot.message:
            bot.type_text("r")
        return True

    return False


@strategy
def quaff_potion(bot: "Bot"):
    items = bot.inventory["potions"]
    for item in items:
        bot.step(A.Command.QUAFF)
        bot.step(item.letter)
        return True

    return False

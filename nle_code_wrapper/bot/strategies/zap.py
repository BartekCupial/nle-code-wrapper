from typing import Callable

from nle.nethack.actions import Command

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def zap(bot: "Bot"):
    bot.step(Command.ZAP)

    # if "What do you want to zap?" in bot.message:
    #     # if we pick correct letter we can then zap which will use the charge
    #         # if we abort we can preserve the charge
    #         # else lose one charge
    #             # correct direction -> effect
    #             # incorrect direction -> no effect
    #     # if we pick incorrect letter game will not use the charge and we exit zapping
    #     return False
    # else:
    #     return False

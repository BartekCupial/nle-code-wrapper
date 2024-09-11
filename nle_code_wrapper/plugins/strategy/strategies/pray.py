from nle.nethack import actions as A

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.plugins.strategy import State, Strategy


@Strategy.wrap
def pray(bot: "Bot", last_pray=State(-1)):
    pray_timeout = 1200

    while True:
        if last_pray.value == -1:
            last_pray.value = bot.blstats.time
            bot.step(A.Command.PRAY)
        elif bot.blstats.time - last_pray.value > pray_timeout:
            last_pray.value = bot.blstats.time
            bot.step(A.Command.PRAY)

        yield

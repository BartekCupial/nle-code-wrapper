from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategy import Panic, State


@Panic.wrap
def lost_hp(bot: "Bot", prev_hp=State(-1)):
    # TODO: we need to check if there was a level up or increase in the hp, maybe max_hp?
    while True:
        if prev_hp.value == -1:
            prev_hp.value = bot.blstats.hitpoints

        if prev_hp.value > bot.blstats.hitpoints:
            prev_hp.value = bot.blstats.hitpoints
            raise BotPanic("lost hp")
        else:
            yield False

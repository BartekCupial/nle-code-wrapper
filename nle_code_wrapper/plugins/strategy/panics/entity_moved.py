from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.plugins.strategy.panic import Panic


def lists_match(list1, list2):
    if len(list1) != len(list2):
        return False
    return all(x == y for x, y in zip(list1, list2))


@Panic.wrap
def entity_moved(bot: "Bot"):
    prev_entities = bot.entities
    while True:
        if prev_entities != bot.entities:
            prev_entities = bot.entities
            raise BotPanic("entities moved")
        else:
            yield False

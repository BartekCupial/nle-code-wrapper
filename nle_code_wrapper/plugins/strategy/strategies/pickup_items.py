from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.plugins.strategy import Strategy


@Strategy.wrap
def pickup_items(bot: "Bot"):
    level = bot.current_level()

    if level.item_objects[bot.entity.position]:
        bot.pickup()
        yield True
    else:
        yield False

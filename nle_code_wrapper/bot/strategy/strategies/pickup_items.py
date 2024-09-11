from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import Strategy
from nle_code_wrapper.utils.utils import coords


@Strategy.wrap
def pickup_items(bot: "Bot"):
    item_coords = coords(bot.glyphs, G.OBJECTS)

    if bot.entity.position in item_coords:
        bot.step(A.Command.PICKUP)
        yield True
    else:
        yield False

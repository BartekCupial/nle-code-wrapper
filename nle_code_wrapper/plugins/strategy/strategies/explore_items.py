from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.plugins.strategy import Strategy
from nle_code_wrapper.utils.utils import coords


@Strategy.wrap
def explore_items(bot: "Bot"):
    level = bot.current_level()
    item_coords = coords(bot.glyphs, G.OBJECTS)
    distances = bot.pathfinder.distances(bot.entity.position)

    # go to closest item which is reachable and unexplored
    item = min(
        (i for i in item_coords if i in distances and not level.was_on[i]),
        key=lambda i: distances[i],
        default=None,
    )

    if item:
        bot.pathfinder.goto(item)
        yield True
    else:
        yield False

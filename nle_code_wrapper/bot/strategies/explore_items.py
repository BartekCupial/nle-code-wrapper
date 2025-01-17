from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils.utils import coords


@strategy
def explore_items(bot: "Bot"):
    """
    explore the map by going to the closest unexplored item
    """
    level = bot.current_level
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
        return True
    else:
        return False

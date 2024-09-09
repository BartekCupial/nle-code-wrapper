from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.plugins.strategy import Strategy


@Strategy.wrap
def goto_items(bot: "Bot"):
    level = bot.current_level()
    item_positions = list(zip(*(level.item_objects > 0).nonzero()))
    distances = bot.pathfinder.distances(bot.entity.position)

    # go to closest item which is reachable and unexplored
    item = min(
        (i for i in item_positions if i in distances),
        key=lambda i: distances[i],
        default=None,
    )

    if item:
        bot.pathfinder.goto(item)
        yield True
    else:
        yield False

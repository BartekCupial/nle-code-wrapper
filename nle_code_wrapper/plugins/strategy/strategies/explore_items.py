from nle_code_wrapper.bot import Bot
from nle_code_wrapper.plugins.strategy import Strategy


@Strategy.wrap
def explore_items(bot: "Bot"):
    level = bot.current_level()
    item_positions = list(zip(*(level.item_objects > 0).nonzero()))
    distances = bot.pathfinder.distances(bot.entity.position)

    # go to closest item which is reachable and unexplored
    item = min(
        (i for i in item_positions if i in distances and not level.was_on[i]),
        key=lambda i: distances[i],
        default=None,
    )

    if item:
        bot.pathfinder.goto(item)
        yield True
    else:
        yield False

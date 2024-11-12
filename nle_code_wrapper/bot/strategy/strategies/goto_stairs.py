from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import Strategy


@Strategy.wrap
def goto_stairs(bot: "Bot"):
    """
    Directs the bot to move towards the stairs on the current level.
    This function attempts to find the coordinates of the stairs down on the current level
    and directs the bot to move towards them using the bot's pathfinder. If a path to
    the stairs is found, the bot will move towards the first set of stairs found.
    Args:
        bot (Bot): The bot instance that will be directed to the stairs.
    Yields:
        bool: True if the bot successfully finds a path to the stairs and starts moving
              towards them, False otherwise.
    """

    level = bot.current_level()
    stairs = level.object_coords(G.STAIR_DOWN)
    if len([s for s in stairs if bot.pathfinder.get_path_to(s)]) > 0:
        bot.pathfinder.goto(stairs[0])
        yield True
    else:
        yield False

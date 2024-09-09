from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.plugins.strategy import Strategy


@Strategy.wrap
def goto_stairs(bot: "Bot"):
    level = bot.current_level()
    stairs = level.object_coords(G.STAIR_DOWN)
    if len([s for s in stairs if bot.pathfinder.get_path_to(s)]) > 0:
        bot.pathfinder.goto(stairs[0])
        yield True
    else:
        yield False

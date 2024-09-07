from nle_code_wrapper.bot import Bot
from nle_code_wrapper.plugins.strategy import Strategy


@Strategy.wrap
def goto_stairs(bot: "Bot"):
    level = bot.current_level()
    if len([s for s in level.stairs if bot.pathfinder.get_path_to(s)]) > 0:
        bot.pathfinder.goto(level.stairs[0])
        yield True
    else:
        yield False

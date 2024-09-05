from nle_code_wrapper.bot import Bot


def goto_stairs(bot: "Bot"):
    level = bot.current_level()
    # if there is no monsters goto stairs
    if len(level.stairs) > 0:
        bot.pathfinder.goto(level.stairs[0])

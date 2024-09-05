from nle_code_wrapper.bot import Bot


def goto_stairs(bot: "Bot"):
    level = bot.current_level()
    if len([s for s in level.stairs if bot.pathfinder.get_path_to(s)]) > 0:
        bot.pathfinder.goto(level.stairs[0])

    yield

from nle_code_wrapper.bot import Bot


def goto_stairs(bot: "Bot"):
    stairs = bot.current_level().stairs
    bot.pathfinder.goto(stairs[0])

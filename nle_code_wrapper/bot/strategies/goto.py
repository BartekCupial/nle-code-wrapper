from nle_code_wrapper.bot import Bot


def goto(bot: "Bot", y: int, x: int) -> bool:
    position = (y, x)
    return bot.pathfinder.goto(position)

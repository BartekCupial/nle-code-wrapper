from typing import Union

from nle.nethack.actions import CompassCardinalDirection, CompassIntercardinalDirection, MiscDirection

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


def direction(
    bot: "Bot", direction: Union[CompassCardinalDirection, CompassIntercardinalDirection, MiscDirection]
) -> bool:
    bot.step(direction)
    return True


@strategy
def west(bot: "Bot"):
    return direction(bot, CompassCardinalDirection.W)


@strategy
def north(bot: "Bot"):
    return direction(bot, CompassCardinalDirection.N)


@strategy
def east(bot: "Bot"):
    return direction(bot, CompassCardinalDirection.E)


@strategy
def south(bot: "Bot"):
    return direction(bot, CompassCardinalDirection.S)


@strategy
def north_east(bot: "Bot"):
    return direction(bot, CompassIntercardinalDirection.NE)


@strategy
def south_east(bot: "Bot"):
    return direction(bot, CompassIntercardinalDirection.SE)


@strategy
def south_west(bot: "Bot"):
    return direction(bot, CompassIntercardinalDirection.SW)


@strategy
def north_west(bot: "Bot"):
    return direction(bot, CompassIntercardinalDirection.NW)


@strategy
def up(bot: "Bot"):
    # go up a staircase
    return direction(bot, MiscDirection.UP)


@strategy
def down(bot: "Bot"):
    # go down a staircase
    return direction(bot, MiscDirection.DOWN)


@strategy
def wait(bot: "Bot"):
    # rest one move while doing nothing / apply to self
    return direction(bot, MiscDirection.WAIT)

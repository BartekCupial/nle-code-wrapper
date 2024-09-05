from typing import TYPE_CHECKING

from nle.nethack import actions as A

from nle_code_wrapper.bot.exceptions import BotPanic

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


def calc_direction(from_y, from_x, to_y, to_x):
    assert abs(from_y - to_y) <= 1 and abs(from_x - to_x) <= 1, ((from_y, from_x), (to_y, to_x))

    ret = ""
    if to_y == from_y + 1:
        ret += "s"
    if to_y == from_y - 1:
        ret += "n"
    if to_x == from_x + 1:
        ret += "e"
    if to_x == from_x - 1:
        ret += "w"
    if ret == "":
        ret = "."

    return ret


def direction(bot: "Bot", dir):
    action = {
        "n": A.CompassDirection.N,
        "s": A.CompassDirection.S,
        "e": A.CompassDirection.E,
        "w": A.CompassDirection.W,
        "ne": A.CompassDirection.NE,
        "se": A.CompassDirection.SE,
        "nw": A.CompassDirection.NW,
        "sw": A.CompassDirection.SW,
        ">": A.MiscDirection.DOWN,
        "<": A.MiscDirection.UP,
        ".": A.MiscDirection.WAIT,
    }[dir]

    bot.step(action)


def move(bot: "Bot", y, x):
    dir = calc_direction(bot.blstats.y, bot.blstats.x, y, x)
    direction(bot, dir)

    if bot.position != (y, x):
        raise BotPanic(
            f'agent position do not match after "move": '
            f"expected ({y}, {x}), got ({bot.entity.position[0]}, {bot.entity.position[1]})"
        )


def goto(bot: "Bot", goal):
    path = bot.pathfinder.get_path_to(goal)
    orig_path = list(path)
    path = orig_path[1:]

    for y, x in path:
        # TODO: add checks if the terrain ahead is still walkable
        # - trap (including holes)
        # - water
        # - lava
        # - boulders
        try:
            move(bot, y, x)
        except BotPanic:
            return False

    return True

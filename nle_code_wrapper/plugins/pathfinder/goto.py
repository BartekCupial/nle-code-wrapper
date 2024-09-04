from nle.nethack import actions as A

from nle_code_wrapper.plugins.pathfinder.movements import Movements


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


def direction(bot, dir):
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


def move(bot, y, x):
    dir = calc_direction(bot.blstats.y, bot.blstats.x, y, x)
    direction(bot, dir)
    # TODO: check that expected position matches the actual one


def goto(bot, goal):
    movements = Movements(bot)
    path = bot.pathfinder.get_path_to(movements, goal)
    orig_path = list(path)
    path = orig_path[1:]

    for y, x in path:
        # TODO: add checks if the terrain ahead is still walkable
        # - trap (including holes)
        # - water
        # - lava
        move(bot, y, x)

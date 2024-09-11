from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import Strategy


@Strategy.wrap
def open_doors(bot: "Bot"):
    level = bot.current_level()
    closed_doors = level.object_coords(G.DOOR_CLOSED)

    reachable_door = min(
        (door for door in closed_doors if bot.pathfinder.reachable_adjacent(bot.entity.position, door)),
        key=lambda door: bot.pathfinder.distance(bot.entity.position, door),
        default=None,
    )

    if reachable_door:
        adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, reachable_door)
        bot.pathfinder.goto(adjacent)
        bot.pathfinder.direction(reachable_door)

        yield True
    else:
        yield False


@Strategy.wrap
def open_doors_kick(bot: "Bot"):
    level = bot.current_level()
    closed_doors = level.object_coords(G.DOOR_CLOSED)

    reachable_door = min(
        (door for door in closed_doors if bot.pathfinder.reachable_adjacent(bot.entity.position, door)),
        key=lambda door: bot.pathfinder.distance(bot.entity.position, door),
        default=None,
    )

    if reachable_door:
        adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, reachable_door)
        bot.pathfinder.goto(adjacent)
        bot.step(A.Command.KICK)
        bot.pathfinder.direction(reachable_door)

        yield True
    else:
        yield False


@Strategy.wrap
def open_doors_key(bot: "Bot"):
    level = bot.current_level()
    closed_doors = level.object_coords(G.DOOR_CLOSED)

    reachable_door = min(
        (door for door in closed_doors if bot.pathfinder.reachable_adjacent(bot.entity.position, door)),
        key=lambda door: bot.pathfinder.distance(bot.entity.position, door),
        default=None,
    )

    if reachable_door:
        adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, reachable_door)
        bot.pathfinder.goto(adjacent)
        bot.step(A.Command.APPLY)

        yield True
    else:
        yield False

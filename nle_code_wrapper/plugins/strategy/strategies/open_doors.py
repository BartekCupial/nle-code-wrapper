from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.plugins.strategy import Strategy


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
        bot.direction(reachable_door)

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
        bot.kick(reachable_door)

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
        bot.apply()

        yield True
    else:
        yield False

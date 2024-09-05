import re

import numpy as np
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot


def open_doors(bot: "Bot"):
    level = bot.current_level()

    closed_doors = level.object_positions(G.DOOR_CLOSED)
    adjacent_to_doors = [bot.pathfinder.reachable_adjacent(bot.entity.position, door) for door in closed_doors]
    # open doors if there is any closed and reachable doors
    if len(closed_doors) > 0 and any(adjacent_to_doors):
        adjacent_distance, reachable_doors = tuple(
            zip(
                *[
                    (bot.pathfinder.distance(bot.entity.position, adjacent), doors)
                    for adjacent, doors in zip(adjacent_to_doors, closed_doors)
                    if adjacent
                ]
            )
        )
        idx = np.argmin(adjacent_distance)
        bot.pathfinder.goto(adjacent_to_doors[idx])
        bot.direction(reachable_doors[idx])

        # if door is locked
        if re.match(".*This door is locked.*", bot.message):
            # TODO: try to open with key or credit card
            bot.kick(reachable_doors[idx])

    yield

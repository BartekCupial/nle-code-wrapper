import itertools

import numpy as np
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.goto import get_other_features, goto_object
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import label_dungeon_features


@strategy
def goto_boulder(bot: "Bot") -> bool:
    boulder = utils.isin(bot.current_level.objects, G.BOULDER)
    positions = np.argwhere(boulder)

    # If no positions, return False
    if len(positions) == 0:
        return False

    # Go to the closest position
    distances = np.sum(np.abs(positions - bot.entity.position), axis=1)
    closest_position = positions[np.argmin(distances)]

    adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, tuple(closest_position))
    return bot.pathfinder.goto(adjacent)


def get_adjacent_boulder(bot: "Bot"):
    bot_pos = bot.entity.position
    for i, j in itertools.product([-1, 0, 1], repeat=2):
        if i == 0 and j == 0:
            continue
        if bot.current_level.objects[bot_pos[0] + i, bot_pos[1] + j] in G.BOULDER:
            return (bot_pos[0] + i, bot_pos[1] + j)
    return None


@strategy
def push_boulder_direction(bot: "Bot", direction) -> bool:
    # 1) check if we are standing next to a boulder
    boulder_pos = get_adjacent_boulder(bot)
    if boulder_pos is None:
        return False

    # 2) push the boulder in direction
    dir = bot.pathfinder.direction_movements[direction]
    opposite_dir = tuple(np.array(dir) * -1)
    bot.pathfinder.goto(tuple(np.array(boulder_pos) + opposite_dir))
    bot.pathfinder.move(tuple(np.array(bot.entity.position) + dir))
    return True


def push_boulder_west(bot: "Bot") -> bool:
    return push_boulder_direction(bot, "west")


def push_boulder_east(bot: "Bot") -> bool:
    return push_boulder_direction(bot, "east")


def push_boulder_north(bot: "Bot") -> bool:
    return push_boulder_direction(bot, "north")


def push_boulder_south(bot: "Bot") -> bool:
    return push_boulder_direction(bot, "south")


def river_detection(bot: "Bot"):
    water = utils.isin(bot.glyphs, frozenset({SS.S_water}))
    labels, num_rooms, num_corridors = label_dungeon_features(bot)
    features, num_features = ndimage.label(labels > 0)
    features_lava, num_lava_features = ndimage.label(np.logical_or(labels > 0, water))
    return features, num_features, features_lava, num_lava_features


def shortest_path_to_water(bot: "Bot", boulder_pos):
    water = utils.isin(bot.glyphs, frozenset({SS.S_water}))
    water_positions = np.argwhere(water)
    if len(water_positions) == 0:
        return None  # no river

    distances = np.sum(np.abs(water_positions - boulder_pos), axis=1)
    closest_position = water_positions[np.argmin(distances)]

    lev = bot.pathfinder.movements.levitating
    bot.pathfinder.movements.levitating = True
    path = bot.pathfinder.get_path_from_to(boulder_pos, tuple(closest_position))
    bot.pathfinder.movements.levitating = lev

    return path


@strategy
def push_boulder_into_river(bot: "Bot") -> bool:
    # 1) check if we are standing next to a boulder
    boulder_pos = get_adjacent_boulder(bot)
    if boulder_pos is None:
        return False

    # 2) find shortest path to the river
    path = shortest_path_to_water(bot, boulder_pos)
    if path is None:
        return False

    # 3) push the boulder into the river
    movements = np.diff(path, axis=0)
    directions = {v: k for k, v in bot.pathfinder.direction_movements.items()}
    for move in movements:
        push_boulder_direction(bot, directions[tuple(move)])

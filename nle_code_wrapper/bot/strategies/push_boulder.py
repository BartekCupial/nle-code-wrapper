import itertools

import numpy as np
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.goto import get_other_features, goto_object
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import label_dungeon_features


def find_furthest_walkable_position(bot: "Bot", dir):
    positions = np.argwhere(bot.current_level.walkable)

    projections = np.dot(positions, dir)
    furthest_index = np.argmax(projections)

    return tuple(positions[furthest_index])


def find_intersections(pos1, pos2):
    return [(pos1[0], pos2[1]), (pos2[0], pos1[1])]


@strategy
def goto_boulder(bot: "Bot") -> bool:
    """
    Moves the agent adjacent to the closest boulder.
    """
    # 1) check if we are standing next to a boulder
    boulder = utils.isin(bot.current_level.objects, G.BOULDER)
    positions = np.argwhere(boulder)
    if len(positions) == 0:
        return False

    # 2) find the position adjacent to a boulder closest to the agent
    distances = np.sum(np.abs(positions - bot.entity.position), axis=1)
    closest_position = positions[np.argmin(distances)]
    adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, tuple(closest_position))

    return bot.pathfinder.goto(adjacent)


@strategy
def goto_boulder_closest_to_river(bot: "Bot") -> bool:
    """
    Moves the agent to closest boulder to river.
    """
    # 1) check if we are standing next to a boulder
    boulder = utils.isin(bot.current_level.objects, G.BOULDER)
    boulder_positions = np.argwhere(boulder)
    if len(boulder_positions) == 0:
        return False  # no boulders

    # 2) check if there is a river
    water = utils.isin(bot.glyphs, frozenset({SS.S_water}))
    water_positions = np.argwhere(water)
    if len(water_positions) == 0:
        return None  # no river

    # 3) find the position adjacent to a boulder closest to the river
    boulder_pos = min(
        boulder_positions,
        key=lambda boulder_pos: np.min(np.sum(np.abs(boulder_pos - water_positions), axis=1)),
        default=None,
    )
    adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, tuple(boulder_pos))

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
    """
    Pushes a boulder one step in a chosen direction, will also move around the boulder if needed
    """
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


def push_boulder_to_pos(bot: "Bot", boulder_pos, target_pos):
    """
    Pushes a boulder to a target position
    """
    # 1) imagine that we are levitating to find the path
    lev = bot.pathfinder.movements.levitating
    bot.pathfinder.movements.levitating = True
    path = bot.pathfinder.get_path_from_to(boulder_pos, target_pos)
    bot.pathfinder.movements.levitating = lev

    # TODO: this doesn't work when we have two boulders next to each other
    # 2) push the boulder to the target position
    movements = np.diff(path, axis=0)
    directions = {v: k for k, v in bot.pathfinder.direction_movements.items()}
    for move in movements:
        push_boulder_direction(bot, directions[tuple(move)])


@strategy
def push_boulder_into_river(bot: "Bot") -> bool:
    """
    Executes a sequence of steps to push adjacent boulder into the river
    """
    # 1) check if we are standing next to a boulder
    boulder_pos = get_adjacent_boulder(bot)
    if boulder_pos is None:
        return False

    # 2) check if there is a river
    water = utils.isin(bot.glyphs, frozenset({SS.S_water}))
    water_positions = np.argwhere(water)
    if len(water_positions) == 0:
        return None  # no river

    # 3) find furthest walkable position to the east (river is to the east)
    #    then add one step to the east to find the target position
    dir = bot.pathfinder.direction_movements["east"]
    river_bridge_pos = find_furthest_walkable_position(bot, dir)
    target_pos = tuple(np.array(river_bridge_pos) + dir)

    # 4) push the boulder into the river
    push_boulder_to_pos(bot, boulder_pos, target_pos)


@strategy
def align_boulder_for_bridge(bot: "Bot") -> bool:
    """
    Moves and positions the boulder with an open spot in a river
    where it can close the gap and contribute to forming a bridge
    """
    # 1) check if we are standing next to a boulder
    boulder_pos = get_adjacent_boulder(bot)
    if boulder_pos is None:
        return False

    # 2) check if there is a river
    water = utils.isin(bot.glyphs, frozenset({SS.S_water}))
    water_positions = np.argwhere(water)
    if len(water_positions) == 0:
        return None  # no river

    # 3) find vertical position which aligns horizontally with furthest water position
    dir = bot.pathfinder.direction_movements["east"]
    river_bridge_pos = find_furthest_walkable_position(bot, dir)
    intersections = find_intersections(boulder_pos, river_bridge_pos)
    target_pos = [pos for pos in intersections if bot.current_level.walkable[pos]][0]

    # 4) align the horizontally boulder with the furthest water position
    push_boulder_to_pos(bot, boulder_pos, target_pos)

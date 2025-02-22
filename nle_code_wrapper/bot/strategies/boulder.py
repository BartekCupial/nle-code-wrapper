import itertools

import numpy as np
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.goto import get_other_features, goto_object
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import label_dungeon_features


def find_nearest_boulder(bot: "Bot"):
    boulders = np.argwhere(utils.isin(bot.glyphs, G.BOULDER))
    distances = bot.pathfinder.distances(bot.entity.position)
    return min(
        ((pos, tuple(boulder)) for boulder in boulders for pos in bot.pathfinder.neighbors(tuple(boulder))),
        key=lambda pair: distances.get(pair[0], np.inf),
        default=None,
    )


@strategy
def goto_boulder(bot: "Bot") -> bool:
    """
    Moves the agent adjacent to the closest boulder.
    """
    adjacent_boulder = find_nearest_boulder(bot)
    if adjacent_boulder:
        bot.pathfinder.goto(adjacent_boulder[0])

        return True
    else:
        return False


@strategy
def goto_boulder_closest_to_river(bot: "Bot") -> bool:
    """
    Moves the agent to closest boulder to river.
    """
    # 1) check if we are standing next to a boulder
    boulder = utils.isin(bot.glyphs, G.BOULDER)
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
    if boulder_pos is None:
        return False

    adjacent = bot.pathfinder.reachable(bot.entity.position, tuple(boulder_pos), adjacent=True)
    if adjacent is None:
        return False

    return bot.pathfinder.goto(adjacent)


def get_adjacent_boulder(bot: "Bot"):
    bot_pos = bot.entity.position
    height, width = bot.glyphs.shape
    for i, j in itertools.product([-1, 0, 1], repeat=2):
        if i == 0 and j == 0:
            continue

        # make sure we don't have out of bounds
        new_x, new_y = bot_pos[0] + i, bot_pos[1] + j
        if not (0 <= new_x < height) or not (0 <= new_y < width):
            continue

        if bot.glyphs[new_x, new_y] in G.BOULDER:
            return (new_x, new_y)
    return None


@strategy
def push_boulder_direction(bot: "Bot", direction) -> bool:
    """
    Pushes a boulder one step in a chosen direction, will also move around the boulder if needed
    """
    # 1) check if we are standing next to a boulder
    boulder_pos = get_adjacent_boulder(bot)
    if boulder_pos is None:
        return False  # no boulders

    # 2) push the boulder in direction
    dir = bot.pathfinder.direction_movements[direction]
    opposite_dir = tuple(np.array(dir) * -1)
    bot.pathfinder.goto(tuple(np.array(boulder_pos) + opposite_dir))
    bot.pathfinder.move(tuple(np.array(bot.entity.position) + dir))

    return True


def push_boulder_west(bot: "Bot") -> bool:
    """
    Pushes a boulder one step westward.
    Tips:
    - will also move around the boulder if needed
    - bot needs to stand near boulder first
    """
    return push_boulder_direction(bot, "west")


def push_boulder_east(bot: "Bot") -> bool:
    """
    Pushes a boulder one step eastward.
    """
    return push_boulder_direction(bot, "east")


def push_boulder_north(bot: "Bot") -> bool:
    """
    Pushes a boulder one step northward.
    """
    return push_boulder_direction(bot, "north")


def push_boulder_south(bot: "Bot") -> bool:
    """
    Pushes a boulder one step southward.
    """
    return push_boulder_direction(bot, "south")


def river_detection(bot: "Bot"):
    water = utils.isin(bot.glyphs, frozenset({SS.S_water}))
    labels, num_rooms, num_corridors = label_dungeon_features(bot)
    features, num_features = ndimage.label(labels > 0)
    features_lava, num_lava_features = ndimage.label(np.logical_or(labels > 0, water))
    return features, num_features, features_lava, num_lava_features


def push_boulder_to_pos(bot: "Bot", boulder_pos, target_pos):
    """
    Pushes a boulder to a target position.
    """
    # 1) imagine that we are levitating to find the path
    lev = bot.movements.levitating
    bot.movements.levitating = True
    path = bot.pathfinder.get_path_from_to(boulder_pos, target_pos)
    bot.movements.levitating = lev
    if not path:
        return False

    # 2) push the boulder to the target position
    movements = np.diff(path, axis=0).tolist()
    first_move = movements.pop(0)
    opposite_dir = tuple(np.array(first_move) * -1)
    bot.pathfinder.goto(tuple(np.array(boulder_pos) + opposite_dir))
    bot.pathfinder.move(tuple(np.array(bot.entity.position) + first_move))
    for move in movements:
        bot.pathfinder.move(tuple(np.array(bot.entity.position) + move))

    return True


@strategy
def push_boulder_into_river(bot: "Bot") -> bool:
    """
    Executes a sequence of steps to push adjacent boulder into the river.
    Tips:
    - bot needs to stand near boulder first
    """
    # 1) check if we are standing next to a boulder
    boulder_pos = get_adjacent_boulder(bot)
    if boulder_pos is None:
        return False  # no boulders

    # 2) check if there is a river
    water = utils.isin(bot.glyphs, frozenset({SS.S_water}))
    water_positions = np.argwhere(water)
    if len(water_positions) == 0:
        return None  # no river

    # 3) find water position exactly to the east of the boulder
    dir = np.array(bot.pathfinder.direction_movements["east"])
    diff = water_positions - boulder_pos
    mask = np.all((diff == 0) & (dir == 0) | (diff * dir > 0) & (dir != 0), axis=1)
    valid_positions = water_positions[mask]
    if len(valid_positions) == 0:
        return None  # no river to the east

    target_pos = valid_positions[np.argmin(np.sum(np.abs(valid_positions - boulder_pos), axis=1))]

    # 4) push the boulder into the river
    return push_boulder_to_pos(bot, boulder_pos, tuple(target_pos))


def find_furthest_reachable_position(bot: "Bot", dir):
    positions, distances = zip(*bot.pathfinder.distances(bot.entity.position).items())
    positions, distances = np.array(positions), np.array(distances)

    # Calculate projections along the direction
    projections = np.dot(positions, dir)

    # filter with maximum projection value
    positions, distances = positions[projections == max(projections)], distances[projections == max(projections)]

    # find the one closest to current position
    return positions[np.argmin(distances)]


def find_intersections(pos1, pos2):
    return [(pos1[0], pos2[1]), (pos2[0], pos1[1])]


@strategy
def align_boulder_for_bridge(bot: "Bot") -> bool:
    """
    Moves and positions the boulder with an open spot in a river
    where it can close the gap and contribute to forming a bridge.
    Tips:
    - bot needs to stand near boulder first
    """
    # 1) check if we are standing next to a boulder
    boulder_pos = get_adjacent_boulder(bot)
    if boulder_pos is None:
        return False  # no boulders

    # 2) check if there is a river
    water = utils.isin(bot.glyphs, frozenset({SS.S_water}))
    water_positions = np.argwhere(water)
    if len(water_positions) == 0:
        return None  # no river

    # 3) find vertical position which aligns horizontally with furthest water position
    dir = bot.pathfinder.direction_movements["east"]
    river_bridge_pos = find_furthest_reachable_position(bot, dir)
    intersections = find_intersections(boulder_pos, river_bridge_pos)

    # boulder is already aligned
    if np.any(np.all(river_bridge_pos == intersections, axis=1)) and np.any(
        np.all(np.array(boulder_pos) == intersections, axis=1)
    ):
        return False

    walkable_target_pos = [pos for pos in intersections if bot.current_level.safe_walkable[pos]]
    if walkable_target_pos == []:  # this can happen if boulder is in the intersection
        return False

    # 4) align the horizontally boulder with the furthest water position
    return push_boulder_to_pos(bot, boulder_pos, walkable_target_pos[0])

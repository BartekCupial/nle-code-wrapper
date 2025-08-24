import networkx as nx
import numpy as np
from nle.nethack import actions as A
from nle_utils.glyph import G
from scipy import ndimage, spatial

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.pathfinder.movements import Movements
from nle_code_wrapper.bot.strategies.goto import goto_closest
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import (
    corridor_detection,
    label_dungeon_features,
    room_detection,
    save_boolean_array_pillow,
)


def find_largest_rectangle(background):
    distances = ndimage.distance_transform_cdt(background)

    # Find the center and radius of the largest inscribed square
    max_distance = distances.max()
    center_coords = np.unravel_index(distances.argmax(), distances.shape)

    center_row, center_col = center_coords
    radius = int(max_distance)

    # Create slices (ensure they're within image bounds)
    top = max(0, center_row - radius)
    bottom = min(background.shape[0], center_row + radius)
    left = max(0, center_col - radius)
    right = min(background.shape[1], center_col + radius)

    row_slice = slice(top, bottom, None)
    col_slice = slice(left, right, None)

    return (row_slice, col_slice)


def find_empty_spaces(bot: "Bot"):
    labels, num_rooms, num_corridors = label_dungeon_features(bot)

    background = labels == 0
    empty_spaces = []

    while True:
        rectangle = find_largest_rectangle(background)
        row_slice, col_slice = rectangle

        # rectangle has to be at least 6x6
        if row_slice.stop - row_slice.start < 6 or col_slice.stop - col_slice.start < 6:
            break

        background[rectangle] = False
        center_of_mass_x = row_slice.start + (row_slice.stop - row_slice.start) // 2
        center_of_mass_y = col_slice.start + (col_slice.stop - col_slice.start) // 2
        area = (row_slice.stop - row_slice.start) * (col_slice.stop - col_slice.start)

        empty_spaces.append(((center_of_mass_x, center_of_mass_y), area))

    return empty_spaces


def find_unsearched_walls(bot: "Bot", search_count_threshold=10):
    labeled_rooms, num_rooms = room_detection(bot)
    labeled_corridors, num_corridors = corridor_detection(bot)

    level = bot.current_level

    rooms = labeled_rooms > 0
    corridors = labeled_corridors > 0
    door_closed = utils.isin(bot.glyphs, G.DOOR_CLOSED)
    walls = utils.isin(bot.glyphs, G.WALL)

    # Find walls adjacent to walkable tiles in current room
    room_walkable = np.logical_and(rooms, level.walkable)

    openings = np.logical_or(corridors, door_closed)
    positions = np.logical_and(
        room_walkable, ndimage.binary_dilation(np.logical_and(walls, np.logical_not(ndimage.binary_dilation(openings))))
    )

    # Exclude already thoroughly searched walls
    unsearched_walls = np.logical_and(positions, level.search_count < search_count_threshold)

    return unsearched_walls


@strategy
def search_room_for_hidden_doors(bot: "Bot") -> bool:
    """
    Searches the rooms for possible hidden doors, will automatically go to the best room and search multiple spots for doors.
    """
    # Dynamic search threshold
    search_count_threshold = 22

    while True:
        unsearched_walls = find_unsearched_walls(bot, search_count_threshold=search_count_threshold)

        if np.any(unsearched_walls) or search_count_threshold > 44:
            break

        search_count_threshold += 22

    empty_spaces = find_empty_spaces(bot)

    if not np.any(unsearched_walls) or len(empty_spaces) == 0:
        return False

    unsearched_walls_indices = np.argwhere(unsearched_walls)

    # Separate positions & areas
    empty_positions = np.array([pos for pos, area in empty_spaces])
    empty_areas = np.array([area for pos, area in empty_spaces])

    # Compute Manhattan distances
    distances = spatial.distance.cdist(unsearched_walls_indices, empty_positions, metric="cityblock")

    # Adjust distances by area: larger spaces are better
    weighted_distances = distances / empty_areas[None, :]

    min_dist_per_wall = weighted_distances.min(axis=1)
    best_wall_idx = min_dist_per_wall.argmin()
    best_wall = unsearched_walls_indices[best_wall_idx]

    # Restrict search to the wall’s room
    labeled_room, num_rooms = room_detection(bot)
    labeled_room_idx = labeled_room[tuple(best_wall)]
    unsearched_walls_indices_room = np.argwhere(np.logical_and(unsearched_walls, labeled_room == labeled_room_idx))

    distances_room = spatial.distance.cdist(unsearched_walls_indices_room, empty_positions, metric="cityblock")
    min_dist_per_wall_room = distances_room.min(axis=1)

    places_to_search = unsearched_walls_indices_room[min_dist_per_wall_room.argsort()]

    while len(places_to_search) > 0:
        wall_idx = places_to_search[0]
        bot.pathfinder.goto(tuple(wall_idx))

        before_search_time = bot.blstats.time
        n_search = 22
        bot.search(n_search)

        if "find a hidden door" in bot.message:
            return True

        if bot.blstats.time - before_search_time < n_search:
            return False

        places_to_search = np.array(
            [p for p in places_to_search if bot.current_level.search_count[tuple(p)] < search_count_threshold]
        )

    return False


@strategy
def search_room_for_hidden_doors_old(bot: "Bot") -> bool:
    """
    Searches the current room's walls for hidden doors by directing the bot to search walls with possible doors.
    Tips:
    - searches spot 10 times (hidden passages might require multiple searches)
    - we need to be in the room to search it (`goto_room`)
    - there is a limit for searching each spot
    """

    labeled_rooms, num_rooms = room_detection(bot)

    # Get current room
    my_position = bot.entity.position
    level = bot.current_level

    # Check if we are in the room
    if labeled_rooms[my_position] == 0:
        return False

    current_room = labeled_rooms == labeled_rooms[my_position]

    # Find walls adjacent to walkable tiles in current room
    room_walkable = np.logical_and(current_room, level.walkable)
    walls = utils.isin(bot.glyphs, G.WALL)
    adjacent_to_walls = np.logical_and(room_walkable, ndimage.binary_dilation(walls))

    # Exclude already thoroughly searched walls
    searchable_walls = np.logical_and(adjacent_to_walls, level.search_count < 40)  # Assume walls need 40 searches

    # Prioritize walls that haven't been searched much
    search_positions = np.argwhere(searchable_walls)

    if len(search_positions) == 0:
        return False

    # Calculate scores based on distance and search count
    distances = bot.pathfinder.distances(bot.entity.position)
    search_distances = [distances.get(tuple(pos), np.inf) for pos in search_positions]
    search_counts = np.array([level.search_count[tuple(pos)] for pos in search_positions])

    corridors_mask, _ = corridor_detection(bot)
    other_rooms_mask = np.logical_and(labeled_rooms > 0, labeled_rooms != labeled_rooms[my_position])
    boundary_mask = np.ones_like(other_rooms_mask)
    boundary_mask[1:-1, 1:-1] = False
    other_mask = other_rooms_mask | boundary_mask | corridors_mask > 0

    # Compute distance from every cell to the nearest cell in a different room.
    # Cells that are far from other rooms yield higher values.
    other_distance_field = ndimage.distance_transform_edt(~other_mask)

    # Get the bonus values for candidate positions (higher value = farther from other rooms)
    other_room_scores = np.array([other_distance_field[tuple(pos)] for pos in search_positions])

    # Define a weight that controls the influence of the distance-from-other-rooms heuristic.
    weight = 2.0  # adjust this factor based on desired sensitivity

    # Combine distance, search count, and negative influence from proximity to other rooms.
    # Lower scores indicate more promising search candidates.
    scores = np.array(search_distances) + search_counts - weight * other_room_scores

    # Select the candidate position with the best (lowest) score
    best_position = search_positions[np.argmin(scores)]
    bot.pathfinder.goto(tuple(best_position))

    bot.search(10)
    return True


@strategy
def search_corridor_for_hidden_doors(bot: "Bot") -> bool:
    """
    Searches the current corridor for hidden doors.
    Tips:
    - diagonal connectivity between corridor will be classified as dead end
    """

    def get_dead_ends(features):
        """
        return positions of the dead ends in the dungeon
        dead end is a position which has on or less cardinal neighbors
        to confirm dead end we check if bot was on this position
        """
        prev_movements = bot.movements
        bot.movements = Movements(bot, cardinal_only=True)
        dead_ends = np.array(
            [
                n
                for n in np.argwhere(features)
                if bot.current_level.was_on[tuple(n)] and len(bot.pathfinder.neighbors(tuple(n))) <= 1
            ]
        )
        bot.movements = prev_movements
        return set(map(tuple, dead_ends))

    labeled_corridors, num_labels = corridor_detection(bot)

    dead_ends = get_dead_ends(labeled_corridors)
    dead_ends = [pos for pos in dead_ends if bot.current_level.search_count[pos] < 44]

    if len(dead_ends) == 0:
        return False

    goto_closest(bot, dead_ends)
    bot.search(22)
    if "find a hidden door" in bot.message or "find a hidden passage" in bot.message:
        return True

    return False


@strategy
def search_for_traps(bot: "Bot") -> bool:
    """
    Search the current position repeatedly for traps.
    """
    bot.search(10)
    return False

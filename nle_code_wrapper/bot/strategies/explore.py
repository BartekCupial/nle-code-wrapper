from typing import Tuple

import numpy as np
from nle_utils.glyph import SS, G
from PIL import Image
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.utils import utils


def print_boolean_array_ascii(arr):
    # Normalize the array to (0, 1)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if min_val == max_val:
        normalized = np.full(arr.shape, 0.5)
    else:
        normalized = (arr - min_val) / (max_val - min_val)
    # Create ASCII visualization
    chars = " ._-=+*#%@"

    for row in normalized:
        line = ""
        for val in row:
            index = int(val * (len(chars) - 1))
            line += chars[index]
        print(line)


def save_boolean_array_pillow(arr):
    # Normalize the array to (0, 1)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if min_val == max_val:
        normalized = np.full(arr.shape, 0.5)
    else:
        normalized = (arr - min_val) / (max_val - min_val)

    normalized = (normalized * 255).astype(np.uint8)
    Image.fromarray(normalized).save("array.png")

    # Create a random colormap (one color for each label)
    unique_values = np.unique(arr)
    num_colors = len(unique_values)  # +1 for background
    colormap = np.random.randint(0, 256, size=(num_colors, 3), dtype=np.uint8)
    # Set background (label 0) to black
    colormap[0] = [0, 0, 0]

    # Convert labeled array to RGB using the colormap
    height, width = arr.shape
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
    for label in unique_values:
        mask = arr == label
        rgb_image[mask] = colormap[label]

    # Create and save PIL Image
    img = Image.fromarray(rgb_image)
    img.save("labeled_rooms.png")


def room_detection(bot: "Bot") -> Tuple[np.ndarray, int]:
    """
    Detect rooms in the dungeon using connected components analysis.

    Args:
        bot: Bot

    Returns:
        Tuple containing:
        - labeled_rooms: numpy array where each room has a unique integer label
        - num_rooms: number of distinct rooms found
    """

    room_floor = frozenset({SS.S_room, SS.S_darkroom})  # TODO: use also SS.S_ndoor?
    rooms = utils.isin(bot.glyphs, G.WALL, G.DOORS, G.BARS, room_floor)
    structure = ndimage.generate_binary_structure(2, 2)
    rooms = ndimage.binary_closing(rooms, structure=structure)
    slices = ndimage.find_objects(ndimage.label(rooms)[0])
    if slices:
        for bbox in slices:
            rooms[bbox] = 1

    labeled_rooms, num_rooms = ndimage.label(rooms, structure=structure)

    return labeled_rooms, num_rooms


def explore_room_systematically(bot: "Bot") -> bool:
    """
    Systematically explores the current room by directing the bot to walkable tiles.

    Args:
        bot (Bot): The bot instance that will perform the exploration.

    Returns:
        bool: True if there are unexplored positions and the bot is directed to one,
              False if all positions in the current room have been explored.

    Details:
        - Detects and labels different rooms in the level
        - Identifies the current room based on bot's position
        - Finds walkable tiles that haven't been explored yet
        - Directs the bot to the closest unexplored position using pathfinding
    """
    labeled_rooms, num_rooms = room_detection(bot)

    # get current room
    my_position = bot.entity.position
    current_room = labeled_rooms == labeled_rooms[my_position]

    # get unexplored positions of the room
    level = bot.current_level
    room_walkable = np.logical_and(current_room, level.walkable)
    room_unexplored = np.logical_and(room_walkable, ~level.was_on)
    unexplored_positions = np.argwhere(room_unexplored)

    # If no unexplored positions, return False
    if len(unexplored_positions) == 0:
        return False

    # Go to the closest unexplored position
    distances = np.sum(np.abs(unexplored_positions - my_position), axis=1)
    closest_position = unexplored_positions[np.argmin(distances)]
    bot.pathfinder.goto(tuple(closest_position))

    return True


def explore_room(bot: "Bot") -> bool:
    """
    Explores the current room by directing the bot to positions that unvail new tiles.

    Args:
        bot (Bot): The bot instance that will perform the exploration.

    Returns:
        bool: True if there are unexplored positions with discovery potential and the bot is directed to one,
              False if all positions in the current room have been explored.

    Details:
        - Detects and labels distinct rooms in the level
        - Identifies the current room based on bot's position
        - Finds walkable tiles that unvail new areas, based on the edges
        - Directs the bot to the closest unexplored position using pathfinding
    """
    labeled_rooms, num_rooms = room_detection(bot)

    # get current room
    my_position = bot.entity.position
    current_room = labeled_rooms == labeled_rooms[my_position]

    # Check if we are in the room
    if labeled_rooms[my_position] == 0:
        return False

    # get unexplored positions of the room
    level = bot.current_level
    structure = ndimage.generate_binary_structure(2, 2)
    unexplored_edges = np.logical_and(ndimage.binary_dilation(~level.seen, structure), level.seen)
    walkable_edges = np.logical_and(unexplored_edges, level.walkable)  # we use level.walkable to exclude walls etc.
    discovery_potential = np.logical_and(walkable_edges, ~level.was_on)
    room_unexplored = np.logical_and(current_room, discovery_potential)
    unexplored_positions = np.argwhere(room_unexplored)

    # If no unexplored positions, return False
    if len(unexplored_positions) == 0:
        return False

    # Go to the closest unexplored position
    distances = np.sum(np.abs(unexplored_positions - my_position), axis=1)
    closest_position = unexplored_positions[np.argmin(distances)]
    bot.pathfinder.goto(tuple(closest_position))

    return True


def search_room_for_hidden_doors(bot: "Bot") -> bool:
    """
    Searches the current room's walls for hidden doors by directing the bot to inspect suspicious spots.

    Args:
        bot (Bot): The bot instance that will perform the search.

    Returns:
        bool: True if potential hidden door spots are found and the bot is directed to one,
              False if no suspicious spots remain in the current room.

    Details:
        - Detects and labels the current room
        - Identifies wall tiles adjacent to walkable tiles
        - Prioritizes walls that haven't been thoroughly inspected
        - Directs bot to search spots multiple times (hidden doors might require multiple searches)
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
    searchable_walls = np.logical_and(adjacent_to_walls, level.search_count < 20)  # Assume walls need 20 searches

    # Prioritize walls that haven't been searched much
    search_positions = np.argwhere(searchable_walls)

    if len(search_positions) == 0:
        return False

    # Calculate scores based on distance and search count
    distances = np.sum(np.abs(search_positions - my_position), axis=1)
    search_counts = np.array([level.search_count[tuple(pos)] for pos in search_positions])

    # Combine distance and search count into a score
    # Prefer closer positions and less searched walls
    scores = distances + search_counts  # Weight distances more heavily

    # Select the position with the best score
    best_position = search_positions[np.argmin(scores)]
    bot.pathfinder.goto(tuple(best_position))

    # Search the spot multiple times
    for _ in range(5):
        bot.search()

    return True


def goto_next_unexplored_room(bot: "Bot") -> bool:
    """
    Directs the bot to the closest unexplored room in the level.

    Args:
        bot (Bot): The bot instance that will perform the room navigation.

    Returns:
        bool: True if an unexplored room is found and the bot is directed to it,
              False if all rooms have been visited.

    Details:
        - Detects and labels different rooms in the level
        - Identifies rooms that haven't been visited yet (no tiles marked as was_on)
        - For each unvisited room, finds the closest position to the bot
        - Directs the bot to the closest position in the nearest unexplored room using pathfinding
        - Background (label 0) is excluded from room consideration
    """
    labeled_rooms, num_rooms = room_detection(bot)

    level = bot.current_level
    unvisited_rooms = []
    # exclude 0 because this is background
    for label in range(1, num_rooms + 1):
        room = labeled_rooms == label
        room = np.logical_and(room, level.walkable)
        # consider only unexplored rooms
        if not np.any(np.logical_and(room, level.was_on)):
            room_positions = np.argwhere(room)
            distances = np.sum(np.abs(room_positions - bot.entity.position), axis=1)
            unvisited_rooms.append((np.min(distances), tuple(room_positions[np.argmin(distances)])))

    closest_position = min((position for distance, position in unvisited_rooms), key=lambda x: x[0], default=None)

    if closest_position:
        bot.pathfinder.goto(closest_position)
        return True
    else:
        return False


def explore_corridor(bot: "Bot") -> bool:
    # Move through corridor (if you are in one)
    # TODO: until you reach a room
    my_position = bot.entity.position
    level = bot.current_level

    corridors = utils.isin(bot.glyphs, frozenset({SS.S_corr, SS.S_litcorr}))
    unexplored_corridors = np.logical_and(corridors, ~level.was_on)
    unexplored_positions = np.argwhere(unexplored_corridors)

    # If no unexplored positions, return False
    if len(unexplored_positions) == 0:
        return False

    # Go to the closest unexplored position
    distances = np.sum(np.abs(unexplored_positions - my_position), axis=1)
    closest_position = unexplored_positions[np.argmin(distances)]
    bot.pathfinder.goto(tuple(closest_position))

    return True


def search_corridor_for_hidden_doors(bot: "Bot") -> bool:
    my_position = bot.entity.position
    level = bot.current_level
    corridors = utils.isin(bot.glyphs, frozenset({SS.S_corr, SS.S_litcorr}))

    # look at dead ends, i.e. positions with only one neighbor
    searchable_positions = np.array(
        [
            n
            for n in np.argwhere(corridors)
            if len(bot.pathfinder.neighbors(tuple(n))) == 1 and level.search_count[tuple(n)] < 20
        ]
    )

    if len(searchable_positions) == 0:
        return False

    # Go to the closest unexplored position
    distances = np.sum(np.abs(searchable_positions - my_position), axis=1)
    search_counts = np.array([level.search_count[tuple(pos)] for pos in searchable_positions])
    # Combine distance and search count into a score
    # Prefer closer positions and less searched deadends
    scores = distances + search_counts  # Weight distances more heavily

    best_position = searchable_positions[np.argmin(scores)]
    bot.pathfinder.goto(tuple(best_position))

    for _ in range(5):
        new_corridors = utils.isin(bot.glyphs, frozenset({SS.S_corr, SS.S_litcorr}))
        if not (corridors == new_corridors).all():
            break
        bot.search()


def search_for_traps(bot: "Bot") -> bool:
    """
    Search the current position repeatedly for traps.

    Returns:
        bool: True if a trap was found
    """
    initial_traps = set(bot.current_level.object_coords(G.TRAPS))

    # Search 20 times
    for _ in range(20):
        bot.search()

        # Check if new traps were discovered
        current_traps = set(bot.current_level.object_coords(G.TRAPS))
        if current_traps - initial_traps:
            return True

    return False


def general_explore(bot: "Bot") -> bool:
    """
    Explore the current level using the bot.
    This function calculates exploration priorities based on several factors
    such as distance from the current position, unexplored areas, and potential
    for discovering new areas. It then navigates the bot to the highest priority
    location.
    Args:
        bot (Bot): The bot instance that will perform the exploration.
    Returns:
        bool: True if there is a location to explore, False if there is nothing
        left to explore.
    """

    level = bot.current_level

    # Create a matrix to store exploration priorities
    exploration_priority = np.zeros(level.seen.shape)

    # Factor 1: Distance from current position
    distances = bot.pathfinder.distances(bot.entity.position)
    distance_matrix = np.full(level.seen.shape, np.inf)
    distance_indices = tuple(np.array(list(distances.keys())).T)
    distance_values = np.array(list(distances.values()))
    distance_matrix[distance_indices] = distance_values

    # Factor 2: Unxplored areas
    unexplored = ~level.was_on

    # Factor 3: Potential for discovering new areas
    # boundary for what we've explored
    structure = ndimage.generate_binary_structure(2, 2)
    unexplored_edges = np.logical_and(ndimage.binary_dilation(~level.seen, structure), level.seen)
    # we use level.walkable to exclude walls etc.
    discovery_potential = np.logical_and(unexplored_edges, level.walkable)

    # Combine factors to create exploration priority
    exploration_priority = (
        (1 / (distance_matrix + 1))  # Prefer closer locations
        * unexplored  # Only consider unexplored areas
        * discovery_potential  # Only conside areas with high discovery potential
    )

    # Set priority to 0 for unreachable or already visited locations
    exploration_priority[~np.isfinite(distance_matrix)] = 0
    exploration_priority[level.was_on] = 0

    # Choose the highest priority location as the goal
    goal = np.unravel_index(np.argmax(exploration_priority), exploration_priority.shape)

    # Navigate to the chosen goal
    if exploration_priority[goal]:
        bot.pathfinder.goto(goal)
        return True
    else:
        # there is nothing to explore
        return False

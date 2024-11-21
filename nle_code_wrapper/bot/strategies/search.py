import numpy as np
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import room_detection, save_boolean_array_pillow
from nle_code_wrapper.utils.utils import coords


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


def general_search(bot: "Bot"):
    """
    Conducts a search operation for the bot to explore the current level.
    The search prioritizes locations based on their distance from the bot's current position
    and the potential for discovering hidden doors or passages. The bot navigates to the
    highest priority location and performs a search action.
    Args:
        bot (Bot): The bot instance performing the search.
    Returns:
        bool: True if the bot navigates to a new location and searches, False if there is
              nothing to explore.
    """

    level = bot.current_level

    # Factor 1: Distance from current position
    distances = bot.pathfinder.distances(bot.entity.position)
    distance_matrix = np.full(level.seen.shape, np.inf)
    distance_indices = tuple(np.array(list(distances.keys())).T)
    distance_values = np.array(list(distances.values()))
    distance_matrix[distance_indices] = distance_values

    # Factor 2: Potential for discovering hidden doors or passages
    structure = ndimage.generate_binary_structure(2, 2)
    room_edges = np.logical_and(~ndimage.binary_erosion(level.walkable, structure), level.walkable)
    discovery_potential = np.logical_and(room_edges, level.walkable)

    # Combine factors to create search priority
    search_priority = (
        (1 / (distance_matrix + 1))  # Prefer closer locations
        * (1 / (level.search_count**2 + 1))  # Decrease search priority where searched
        * discovery_potential  # Only conside areas with high discovery potential
    )

    # Set priority to 0 for unreachable or already visited locations
    search_priority[~np.isfinite(distance_matrix)] = 0
    # search_priority[level.search_count <= bot.max_search_count] = 0

    # Choose the highest priority location as the goal
    goal = np.unravel_index(np.argmax(search_priority), search_priority.shape)

    # Navigate to the chosen goal
    if search_priority[goal]:
        bot.pathfinder.goto(goal)
        bot.search()
        return True
    else:
        # there is nothing to explore
        return False

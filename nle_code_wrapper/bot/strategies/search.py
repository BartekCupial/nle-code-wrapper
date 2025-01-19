import networkx as nx
import numpy as np
from nle_utils.glyph import G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.goto import goto_closest
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import corridor_detection, room_detection, save_boolean_array_pillow


@strategy
def search_room_for_hidden_doors(bot: "Bot") -> bool:
    """
    Searches the current room's walls for hidden doors by directing the bot to search walls with possible doors.
    Tips:
    - searches spot 5 times (hidden passages might require multiple searches)
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
    distances = np.sum(np.abs(search_positions - my_position), axis=1)
    search_counts = np.array([level.search_count[tuple(pos)] for pos in search_positions])

    # Combine distance and search count into a score
    # Prefer closer positions and less searched walls
    scores = distances + search_counts  # Weight distances more heavily

    # Select the position with the best score
    best_position = search_positions[np.argmin(scores)]
    bot.pathfinder.goto(tuple(best_position))

    # Search the spot multiple times
    walls = utils.isin(bot.glyphs, G.WALL)
    for _ in range(5):
        # break if doors are found
        new_walls = utils.isin(bot.glyphs, G.WALL)
        if not (walls == new_walls).all():
            break
        bot.search()

    return True


@strategy
def search_corridor_for_hidden_doors(bot: "Bot") -> bool:
    """
    Searches the current corridor for hidden doors by directing the bot to search dead ends of the corridor.
    Tips:
    - searches spot 5 times (hidden passages might require multiple searches)
    - diagonal connectivity between corridor will be classified as dead end
    - we need to be in the corridor to search it (`goto_corridor`)
    - there is a limit for searching each spot
    """

    my_position = bot.entity.position
    level = bot.current_level

    labeled_corridors, num_labels = corridor_detection(bot)
    current_corridor = labeled_corridors == labeled_corridors[my_position]

    # Check if we are in the corridor
    if labeled_corridors[my_position] == 0:
        return False

    # look at dead ends, i.e. positions with only one neighbor
    graph = bot.pathfinder.create_movements_graph(my_position, cardinal_only=True)

    positions = nx.get_node_attributes(graph, "positions")
    searchable_positions = [positions[node] for node, degree in nx.degree(graph) if degree <= 1]
    searchable_positions = [pos for pos in searchable_positions if level.search_count[pos] < 40]
    searchable_positions = [pos for pos in searchable_positions if current_corridor[pos]]

    if len(searchable_positions) == 0:
        return False

    goto_closest(bot, searchable_positions)

    # Search the spot multiple times
    labeled_corridors, num_labels = corridor_detection(bot)
    for _ in range(5):
        # break if doors are found
        new_labeled_corridors, _ = corridor_detection(bot)
        if not (labeled_corridors == new_labeled_corridors).all():
            break
        bot.search()

    return True


@strategy
def search_for_traps(bot: "Bot") -> bool:
    """
    Search the current position repeatedly for traps.
    """
    initial_traps = set(bot.current_level.object_coords(G.TRAPS))

    # TODO: make use of search counter
    for _ in range(5):
        bot.search()

        # Check if new traps were discovered
        current_traps = set(bot.current_level.object_coords(G.TRAPS))
        if current_traps - initial_traps:
            return True

    return False


@strategy
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

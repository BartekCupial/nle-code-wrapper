import networkx as nx
import numpy as np
from nle_utils.glyph import G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.pathfinder.movements import Movements
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
    distances = bot.pathfinder.distances(bot.entity.position)
    search_distances = [distances.get(tuple(pos), np.inf) for pos in search_positions]
    search_counts = np.array([level.search_count[tuple(pos)] for pos in search_positions])

    # Combine distance and search count into a score
    # Prefer closer positions and less searched walls
    scores = search_distances + search_counts  # Weight distances more heavily

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

    bot.movements = Movements(bot, cardinal_only=True)

    my_position = bot.entity.position
    level = bot.current_level

    labeled_corridors, num_labels = corridor_detection(bot)
    current_corridor = labeled_corridors == labeled_corridors[my_position]

    # Check if we are in the corridor
    if labeled_corridors[my_position] == 0:
        return False

    # look at dead ends, i.e. positions with only one neighbor
    graph = bot.pathfinder.create_movements_graph(my_position)

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

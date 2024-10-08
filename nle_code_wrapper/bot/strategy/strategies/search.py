import numpy as np
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import Strategy


@Strategy.wrap
def search(bot: "Bot"):
    level = bot.current_level()

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
        yield True
    else:
        # there is nothing to explore
        yield False

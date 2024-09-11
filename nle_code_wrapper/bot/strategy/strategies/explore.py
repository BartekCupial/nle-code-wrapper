import numpy as np
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import Strategy


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


@Strategy.wrap
def explore(bot: "Bot"):
    level = bot.current_level()

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
        (1 / (distance_matrix + 1))
        * unexplored  # Prefer closer locations
        * discovery_potential  # Only consider unexplored areas  # Prefer areas with high discovery potential
    )

    # Set priority to 0 for unreachable or already visited locations
    exploration_priority[~np.isfinite(distance_matrix)] = 0
    exploration_priority[level.was_on] = 0

    # Choose the highest priority location as the goal
    goal = np.unravel_index(np.argmax(exploration_priority), exploration_priority.shape)

    # Navigate to the chosen goal
    if exploration_priority[goal]:
        bot.pathfinder.goto(goal)
        yield True
    else:
        # there is nothing to explore
        yield False

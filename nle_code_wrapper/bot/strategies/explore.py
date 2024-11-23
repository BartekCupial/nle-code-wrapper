import numpy as np
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.goto import goto_closest
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils.strategies import corridor_detection, room_detection, save_boolean_array_pillow


@strategy
def explore(bot: "Bot", feature_detection):
    """
    Explores the current feature by directing the bot to positions that unvail new tiles.

    Args:
        bot (Bot): The bot instance that will perform the exploration.

    Returns:
        bool: True if there are unexplored positions with discovery potential and the bot is directed to one,
              False if all positions in the current feature have been explored.

    Details:
        - Detects and labels distinct features in the level
        - Identifies the current feature based on bot's position
        - Finds walkable tiles that unvail new areas, based on the edges
        - Directs the bot to the closest unexplored position using pathfinding
    """
    feature_labels, num_labels = feature_detection(bot)

    # get current feature
    my_position = bot.entity.position
    level = bot.current_level
    current_feature = feature_labels == feature_labels[my_position]

    # Check if we are in the feature
    if feature_labels[my_position] == 0:
        return False

    # get unexplored positions of the room
    structure = ndimage.generate_binary_structure(2, 2)
    unexplored_edges = np.logical_and(ndimage.binary_dilation(~level.seen, structure), level.seen)
    walkable_edges = np.logical_and(unexplored_edges, level.walkable)  # we use level.walkable to exclude walls etc.
    discovery_potential = np.logical_and(walkable_edges, ~level.was_on)
    feature_unexplored = np.logical_and(current_feature, discovery_potential)
    unexplored_positions = np.argwhere(feature_unexplored)

    return goto_closest(bot, unexplored_positions)


@strategy
def explore_systematically(bot: "Bot", feature_detection):
    """
    Systematically explores the current feature by directing the bot to walkable tiles.

    Args:
        bot (Bot): The bot instance that will perform the exploration.

    Returns:
        bool: True if there are unexplored positions and the bot is directed to one,
              False if all positions in the current feature have been explored.

    Details:
        - Detects and labels different features in the level
        - Identifies the current feature based on bot's position
        - Finds walkable tiles that haven't been explored yet
        - Directs the bot to the closest unexplored position using pathfinding
    """
    labeled_features, num_labels = feature_detection(bot)

    # get current feature
    my_position = bot.entity.position
    level = bot.current_level
    current_feature = labeled_features == labeled_features[my_position]

    # Check if we are in the feature
    if labeled_features[my_position] == 0:
        return False

    # get unexplored positions of the room
    feature_walkable = np.logical_and(current_feature, level.walkable)
    feature_unexplored = np.logical_and(feature_walkable, ~level.was_on)
    unexplored_positions = np.argwhere(feature_unexplored)

    return goto_closest(bot, unexplored_positions)


def explore_room(bot: "Bot") -> bool:
    return explore(bot, room_detection)


def explore_corridor(bot: "Bot") -> bool:
    return explore(bot, corridor_detection)


def explore_room_systematically(bot: "Bot") -> bool:
    return explore_systematically(bot, room_detection)


def explore_corridor_systematically(bot: "Bot") -> bool:
    return explore_systematically(bot, corridor_detection)


@strategy
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

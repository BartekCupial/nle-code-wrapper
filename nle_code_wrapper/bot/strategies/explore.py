from typing import Callable, Union

import numpy as np
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.goto import goto_closest
from nle_code_wrapper.bot.strategy import repeat, repeat_n_times, repeat_until_discovery, strategy
from nle_code_wrapper.utils.strategies import corridor_detection, room_detection, save_boolean_array_pillow


def get_revelable_positions(bot: "Bot", labeled_features):
    """
    Finds walkable tiles that unvail new areas, based on the edges
    """
    # get current feature
    level = bot.current_level
    # current_feature = labeled_features == labeled_features[bot.entity.position]

    # get unexplored positions of the room
    structure = ndimage.generate_binary_structure(2, 2)
    unexplored_edges = np.logical_and(ndimage.binary_dilation(~level.seen, structure), level.seen)
    walkable_edges = np.logical_and(unexplored_edges, level.walkable)  # we use level.walkable to exclude walls etc.
    discovery_potential = np.logical_and(walkable_edges, ~level.was_on)
    feature_unexplored = np.logical_and(labeled_features, discovery_potential)
    unexplored_positions = np.argwhere(feature_unexplored)

    return unexplored_positions


def get_unvisited_positions(bot: "Bot", labeled_features):
    """
    Finds walkable tiles that haven't been explored yet
    """
    # get current feature
    level = bot.current_level
    current_feature = labeled_features == labeled_features[bot.entity.position]

    # get unexplored positions of the room
    feature_walkable = np.logical_and(current_feature, level.walkable)
    feature_unexplored = np.logical_and(feature_walkable, ~level.was_on)
    unexplored_positions = np.argwhere(feature_unexplored)

    return unexplored_positions


def explore_once(
    bot: "Bot", feature_detection: Union[corridor_detection, room_detection], get_positions: Callable, direction: str
):
    """
    Explores the current feature by directing the bot to positions to explore.

    Args:
        bot (Bot): The bot instance that will perform the exploration.

    Returns:
        bool: True if there are unexplored positions with discovery potential and the bot is directed to one,
              False if all positions in the current feature have been explored.

    Details:
        - Detects and labels distinct features in the level
        - Identifies the current feature based on bot's position
        - Finds positions to explore
        - Directs the bot to the closest unexplored position using pathfinding
    """
    feature_labels, num_labels = feature_detection(bot)

    # Check if we are in the feature
    # if feature_labels[bot.entity.position] == 0:
    #     return False

    unexplored_positions = get_positions(bot, feature_labels)

    direction_filters = {
        "west": lambda pos: pos[1] < bot.entity.position[1],
        "east": lambda pos: pos[1] > bot.entity.position[1],
        "north": lambda pos: pos[0] < bot.entity.position[0],
        "south": lambda pos: pos[0] > bot.entity.position[0],
        "all": lambda pos: True,
    }

    filter_func = direction_filters.get(direction.lower())
    if filter_func:
        unexplored_positions = np.array([position for position in unexplored_positions if filter_func(position)])
        return goto_closest(bot, unexplored_positions)
    return False


@strategy
@repeat_n_times(5)
def explore_five(bot: "Bot", *args, **kwargs):
    return explore_once(bot, *args, **kwargs)


@strategy
@repeat_until_discovery
def explore_discovery(bot: "Bot", *args, **kwargs):
    return explore_once(bot, *args, **kwargs)


@strategy
@repeat
def explore_complete(bot: "Bot", *args, **kwargs):
    return explore_once(bot, *args, **kwargs)


explore = explore_discovery


def explore_room(bot: "Bot") -> bool:
    """
    Explores undiscovered tiles of the room we are in, starting from the closest ones.
    Tips:
    - we will explore until something appears (monster, item, etc) or until there is nothing to explore in current room
    - doors are not treated as part of the room
    - corridors and rooms are labeled using connected components without diagonal connectivity
    """
    return explore(bot, room_detection, get_revelable_positions, "all")


def explore_room_west(bot: "Bot") -> bool:
    """
    Similar to `explore_room`, but filters undiscovered tiles westward.
    """
    return explore(bot, room_detection, get_revelable_positions, "west")


def explore_room_east(bot: "Bot") -> bool:
    """
    Similar to `explore_room`, but filters undiscovered tiles eastward.
    """
    return explore(bot, room_detection, get_revelable_positions, "east")


def explore_room_north(bot: "Bot") -> bool:
    """
    Similar to `explore_room`, but filters undiscovered tiles northward.
    """
    return explore(bot, room_detection, get_revelable_positions, "north")


def explore_room_south(bot: "Bot") -> bool:
    """
    Similar to `explore_room`, but filters undiscovered tiles southward.
    """
    return explore(bot, room_detection, get_revelable_positions, "south")


def explore_corridor(bot: "Bot") -> bool:
    """
    Explores undiscovered tiles of the corridor we are in, starting from the closest ones.
    Tips:
    - we will explore until something appears (monster, item, etc) or until there is nothing to explore in current corridor
    - doors are treated as part of the corridor
    - corridors and rooms are labeled using connected components without diagonal connectivity
    """
    return explore(bot, corridor_detection, get_revelable_positions, "all")


def explore_corridor_west(bot: "Bot") -> bool:
    """
    Similar to `explore_corridor`, but filters undiscovered tiles westward.
    """
    return explore(bot, corridor_detection, get_revelable_positions, "west")


def explore_corridor_east(bot: "Bot") -> bool:
    """
    Similar to `explore_corridor`, but filters undiscovered tiles eastward.
    """
    return explore(bot, corridor_detection, get_revelable_positions, "east")


def explore_corridor_north(bot: "Bot") -> bool:
    """
    Similar to `explore_corridor`, but filters undiscovered tiles northward.
    """
    return explore(bot, corridor_detection, get_revelable_positions, "north")


def explore_corridor_south(bot: "Bot") -> bool:
    """
    Similar to `explore_corridor`, but filters undiscovered tiles southward.
    """
    return explore(bot, corridor_detection, get_revelable_positions, "south")


def explore_room_systematically(bot: "Bot") -> bool:
    return explore(bot, room_detection, get_unvisited_positions, "all")


def explore_room_systematically_west(bot: "Bot") -> bool:
    return explore(bot, room_detection, get_unvisited_positions, "west")


def explore_room_systematically_east(bot: "Bot") -> bool:
    return explore(bot, room_detection, get_unvisited_positions, "east")


def explore_room_systematically_north(bot: "Bot") -> bool:
    return explore(bot, room_detection, get_unvisited_positions, "north")


def explore_room_systematically_south(bot: "Bot") -> bool:
    return explore(bot, room_detection, get_unvisited_positions, "south")


def explore_corridor_systematically(bot: "Bot") -> bool:
    return explore(bot, corridor_detection, get_unvisited_positions, "all")


def explore_corridor_systematically_west(bot: "Bot") -> bool:
    return explore(bot, corridor_detection, get_unvisited_positions, "west")


def explore_corridor_systematically_east(bot: "Bot") -> bool:
    return explore(bot, corridor_detection, get_unvisited_positions, "east")


def explore_corridor_systematically_north(bot: "Bot") -> bool:
    return explore(bot, corridor_detection, get_unvisited_positions, "north")


def explore_corridor_systematically_south(bot: "Bot") -> bool:
    return explore(bot, corridor_detection, get_unvisited_positions, "south")

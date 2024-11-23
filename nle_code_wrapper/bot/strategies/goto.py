import numpy as np
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import corridor_detection, room_detection, save_boolean_array_pillow
from nle_code_wrapper.utils.utils import coords


def goto(bot: "Bot", y: int, x: int) -> bool:
    position = (y, x)
    return bot.pathfinder.goto(position)


def goto_closest(bot, positions):
    # If no positions, return False
    if len(positions) == 0:
        return False

    # Go to the closest position
    distances = np.sum(np.abs(positions - bot.entity.position), axis=1)
    closest_position = positions[np.argmin(distances)]
    bot.pathfinder.goto(tuple(closest_position))

    return True


@strategy
def goto_closest_staircase_down(bot: "Bot") -> bool:
    """
    Directs the bot to move towards the stairs on the current level.
    This function attempts to find the coordinates of the stairs down on the current level
    and directs the bot to move towards them using the bot's pathfinder. If a path to
    the stairs is found, the bot will move towards the first set of stairs found.
    Args:
        bot (Bot): The bot instance that will be directed to the stairs.
    Returns:
        bool: True if the bot successfully finds a path to the stairs and starts moving
              towards them, False otherwise.
    """
    stair = utils.isin(bot.current_level.objects, G.STAIR_DOWN)
    stair_positions = np.argwhere(stair)
    return goto_closest(bot, stair_positions)


@strategy
def goto_closest_staircase_up(bot: "Bot") -> bool:
    """
    Directs the bot to move towards the stairs on the current level.
    This function attempts to find the coordinates of the stairs down on the current level
    and directs the bot to move towards them using the bot's pathfinder. If a path to
    the stairs is found, the bot will move towards the first set of stairs found.
    Args:
        bot (Bot): The bot instance that will be directed to the stairs.
    Returns:
        bool: True if the bot successfully finds a path to the stairs and starts moving
              towards them, False otherwise.
    """
    stair = utils.isin(bot.current_level.objects, G.STAIR_UP)
    stair_positions = np.argwhere(stair)
    return goto_closest(bot, stair_positions)


@strategy
def goto_items(bot: "Bot"):
    """
    Go to the closest item which is reachable and unexplored.

    Args:
        bot (Bot): The bot instance.

    Returns:
        bool: Whether the bot has found an item to go to.
    """
    item_coords = coords(bot.glyphs, G.OBJECTS)
    distances = bot.pathfinder.distances(bot.entity.position)

    # go to closest item which is reachable and unexplored
    item = min(
        (i for i in item_coords if i in distances),
        key=lambda i: distances[i],
        default=None,
    )

    if item:
        bot.pathfinder.goto(item)
        return True
    else:
        return False


def get_other_features(bot: "Bot", feature_detection):
    labeled_features, num_labels = feature_detection(bot)

    my_position = bot.entity.position
    level = bot.current_level
    unvisited_features = []
    # exclude 0 because this is background
    for label in range(1, num_labels + 1):
        feature = labeled_features == label
        feature = np.logical_and(feature, level.walkable)
        # consider rooms which we are not in
        if not label == labeled_features[my_position]:
            feature_positions = np.argwhere(feature)
            distances = np.sum(np.abs(feature_positions - my_position), axis=1)
            unvisited_features.append(tuple(feature_positions[np.argmin(distances)]))

    return np.array(unvisited_features)


@strategy
def goto_closest_feature_direction(bot: "Bot", direction: str, feature_detection) -> bool:
    """
    Directs the bot to the closest room in the level.

    Args:
        bot (Bot): The bot instance that will perform the room navigation.

    Returns:
        bool: True if an room is found and the bot is directed to it,
              False if there is no room to visite.

    Details:
        - Detects and labels different rooms in the level
        - Identifies rooms (no tiles marked as was_on)
        - For each room, finds the closest position to the bot
        - Directs the bot to the closest position in the nearest room using pathfinding
        - Background (label 0) is excluded from room consideration

    Note: it's possible that closest room will not be reachable!
    This will result in BotPanic and this is by design.
    """
    unvisited_rooms = get_other_features(bot, feature_detection)

    direction_filters = {
        "west": lambda pos: pos[1] < bot.entity.position[1],
        "east": lambda pos: pos[1] > bot.entity.position[1],
        "north": lambda pos: pos[0] < bot.entity.position[0],
        "south": lambda pos: pos[0] > bot.entity.position[0],
        "all": lambda pos: True,
    }

    filter_func = direction_filters.get(direction.lower())
    if filter_func:
        unvisited_rooms = np.array([room_position for room_position in unvisited_rooms if filter_func(room_position)])
        return goto_closest(bot, unvisited_rooms)
    return False


@strategy
def goto_closest_unexplored_feature(bot: "Bot", feature_detection) -> bool:
    """
    Directs the bot to the closest unexplored feature in the level.

    Args:
        bot (Bot): The bot instance that will perform the room navigation.

    Returns:
        bool: True if an unexplored feature is found and the bot is directed to it,
              False if all features have been visited.

    Details:
        - Detects and labels different features in the level
        - Identifies features that haven't been visited yet (no tiles marked as was_on)
        - For each unvisited features, finds the closest position to the bot
        - Directs the bot to the closest position in the nearest unexplored features using pathfinding
        - Background (label 0) is excluded from features consideration
    """
    labeled_features, num_labels = feature_detection(bot)

    level = bot.current_level
    unvisited_features = []
    # exclude 0 because this is background
    for label in range(1, num_labels + 1):
        feature = labeled_features == label
        feature = np.logical_and(feature, level.walkable)
        # consider only unexplored features
        if not np.any(np.logical_and(feature, level.was_on)):
            feature_positions = np.argwhere(feature)
            distances = np.sum(np.abs(feature_positions - bot.entity.position), axis=1)
            unvisited_features.append(tuple(feature_positions[np.argmin(distances)]))
    unvisited_features = np.array(unvisited_features)

    return goto_closest(bot, unvisited_features)


def goto_closest_unexplored_room(bot: "Bot") -> bool:
    return goto_closest_unexplored_feature(bot, room_detection)


def goto_closest_unexplored_corridor(bot: "Bot") -> bool:
    return goto_closest_unexplored_feature(bot, corridor_detection)


def goto_closest_corridor_west(bot: "Bot") -> bool:
    return goto_closest_feature_direction(bot, "west", corridor_detection)


def goto_closest_corridor_east(bot: "Bot") -> bool:
    return goto_closest_feature_direction(bot, "east", corridor_detection)


def goto_closest_corridor_north(bot: "Bot") -> bool:
    return goto_closest_feature_direction(bot, "north", corridor_detection)


def goto_closest_corridor_south(bot: "Bot") -> bool:
    return goto_closest_feature_direction(bot, "south", corridor_detection)


def goto_closest_corridor(bot: "Bot") -> bool:
    return goto_closest_feature_direction(bot, "all", corridor_detection)


def goto_closest_room_west(bot: "Bot") -> bool:
    return goto_closest_feature_direction(bot, "west", room_detection)


def goto_closest_room_east(bot: "Bot") -> bool:
    return goto_closest_feature_direction(bot, "east", room_detection)


def goto_closest_room_north(bot: "Bot") -> bool:
    return goto_closest_feature_direction(bot, "north", room_detection)


def goto_closest_room_south(bot: "Bot") -> bool:
    return goto_closest_feature_direction(bot, "south", room_detection)


def goto_closest_room(bot: "Bot") -> bool:
    return goto_closest_feature_direction(bot, "all", room_detection)

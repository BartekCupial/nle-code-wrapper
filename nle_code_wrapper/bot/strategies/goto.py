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
    positions = np.asanyarray(positions)

    # If no positions, return False
    if len(positions) == 0:
        return False

    # Go to the closest position
    distances = np.sum(np.abs(positions - bot.entity.position), axis=1)
    closest_position = positions[np.argmin(distances)]
    bot.pathfinder.goto(tuple(closest_position))

    return True


def goto_object(bot: "Bot", object_type: frozenset[int]) -> bool:
    """
    Directs the bot to move towards the object on the current level.
    This function attempts to find the coordinates of the object on the current level
    and directs the bot to move towards them using the bot's pathfinder. If a path to
    the object is found, the bot will move towards the first object found.
    Args:
        bot (Bot): The bot instance that will be directed to the object.
    Returns:
        bool: True if the bot successfully finds a path to the object and starts moving
              towards it, False otherwise.
    """
    item = utils.isin(bot.current_level.objects, object_type)
    item_positions = np.argwhere(item)
    return goto_closest(bot, item_positions)


def goto_glyph(bot: "Bot", object_type: frozenset[int]) -> bool:
    """
    Directs the bot to move towards the object on the current level.
    This function attempts to find the coordinates of the object on the current level
    and directs the bot to move towards them using the bot's pathfinder. If a path to
    the object is found, the bot will move towards the first object found.
    Args:
        bot (Bot): The bot instance that will be directed to the object.
    Returns:
        bool: True if the bot successfully finds a path to the object and starts moving
              towards it, False otherwise.
    """
    item = utils.isin(bot.glyphs, object_type)
    item_positions = np.argwhere(item)
    return goto_closest(bot, item_positions)


@strategy
def goto_item(bot: "Bot") -> bool:
    return goto_glyph(bot, G.ITEMS)


@strategy
def goto_staircase_down(bot: "Bot") -> bool:
    return goto_object(bot, G.STAIR_DOWN)


@strategy
def goto_staircase_up(bot: "Bot") -> bool:
    return goto_object(bot, G.STAIR_UP)


def get_other_features(bot: "Bot", feature_detection):
    labeled_features, num_labels = feature_detection(bot)

    # if there is only one feature (background), return empty array
    if (labeled_features == labeled_features[0][0]).all():
        return np.array([])

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


def goto_feature_direction(bot: "Bot", direction: str, feature_detection) -> bool:
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


def goto_unexplored_feature(bot: "Bot", feature_detection) -> bool:
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

    # if there is only one feature (background), return empty array
    if (labeled_features == labeled_features[0][0]).all():
        return False

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


@strategy
def goto_unexplored_room(bot: "Bot") -> bool:
    return goto_unexplored_feature(bot, room_detection)


@strategy
def goto_unexplored_corridor(bot: "Bot") -> bool:
    return goto_unexplored_feature(bot, corridor_detection)


@strategy
def goto_corridor_west(bot: "Bot") -> bool:
    return goto_feature_direction(bot, "west", corridor_detection)


@strategy
def goto_corridor_east(bot: "Bot") -> bool:
    return goto_feature_direction(bot, "east", corridor_detection)


@strategy
def goto_corridor_north(bot: "Bot") -> bool:
    return goto_feature_direction(bot, "north", corridor_detection)


@strategy
def goto_corridor_south(bot: "Bot") -> bool:
    return goto_feature_direction(bot, "south", corridor_detection)


@strategy
def goto_corridor(bot: "Bot") -> bool:
    return goto_feature_direction(bot, "all", corridor_detection)


@strategy
def goto_room_west(bot: "Bot") -> bool:
    return goto_feature_direction(bot, "west", room_detection)


@strategy
def goto_room_east(bot: "Bot") -> bool:
    return goto_feature_direction(bot, "east", room_detection)


@strategy
def goto_room_north(bot: "Bot") -> bool:
    return goto_feature_direction(bot, "north", room_detection)


@strategy
def goto_room_south(bot: "Bot") -> bool:
    return goto_feature_direction(bot, "south", room_detection)


@strategy
def goto_room(bot: "Bot") -> bool:
    return goto_feature_direction(bot, "all", room_detection)

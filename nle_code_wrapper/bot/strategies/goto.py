import numpy as np
from nle.nethack import actions as A
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import corridor_detection, room_detection, save_boolean_array_pillow


def goto_closest(bot: "Bot", positions):
    positions = np.asanyarray(positions)

    # If no positions, return False
    if len(positions) == 0:
        return False

    # Go to the closest position
    distances = bot.pathfinder.distances(bot.entity.position)
    closest_position = min(
        (tuple(pos) for pos in positions if distances.get(tuple(pos), np.inf) < np.inf),
        key=lambda pos: distances[pos],
        default=None,
    )
    if closest_position is None:
        return False

    bot.pathfinder.goto(closest_position)
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


def get_other_features(bot: "Bot", feature_detection):
    labeled_features, num_labels = feature_detection(bot)

    # if there is only one feature (background), return empty array
    if (labeled_features == labeled_features[0][0]).all():
        return np.array([])

    my_position = bot.entity.position
    distances = bot.pathfinder.distances(my_position)
    level = bot.current_level
    unvisited_features = []
    # exclude 0 because this is background
    for label in range(1, num_labels + 1):
        feature = labeled_features == label
        feature = np.logical_and(feature, level.walkable)
        # consider rooms which we are not in
        if not label == labeled_features[my_position]:
            feature_positions = np.argwhere(feature)
            closest_position = min(
                (tuple(pos) for pos in feature_positions),
                key=lambda pos: distances.get(tuple(pos), np.inf),
                default=None,
            )
            unvisited_features.append(closest_position)

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

    my_position = bot.entity.position
    distances = bot.pathfinder.distances(my_position)
    level = bot.current_level
    unvisited_features = []
    # exclude 0 because this is background
    for label in range(1, num_labels + 1):
        feature = labeled_features == label
        feature = np.logical_and(feature, level.walkable)
        # consider only unexplored features
        if not np.any(np.logical_and(feature, level.was_on)):
            feature_positions = np.argwhere(feature)
            closest_position = min(
                (tuple(pos) for pos in feature_positions),
                key=lambda pos: distances.get(tuple(pos), np.inf),
                default=None,
            )
            unvisited_features.append(closest_position)
    unvisited_features = np.array(unvisited_features)

    return goto_closest(bot, unvisited_features)


@strategy
def goto_corpse(bot: "Bot"):
    """
    Moves the agent to the closest corpse
    """
    return goto_glyph(bot, G.CORPSES)


@strategy
def descend_stairs(bot: "Bot") -> bool:
    """
    Navigates to and descends the nearest downward staircase.
    """
    features = bot.terrain_features[bot.blstats.dungeon_number, bot.blstats.level_number].get("features", {})
    feature = features.get("stairs down", None)

    if feature is not None:
        distances = bot.pathfinder.distances(bot.entity.position)
        closest_feature = min(
            (tuple(f) for f in feature if distances.get(tuple(f))),
            key=lambda f: distances.get(f, np.inf),
            default=None,
        )

        if closest_feature:
            bot.pathfinder.goto(closest_feature)
            bot.step(A.MiscDirection.DOWN)
            return True

        return False

    else:
        prev_level = bot.blstats.depth
        bot.step(A.MiscDirection.DOWN)
        curr_level = bot.blstats.depth

        return curr_level > prev_level


@strategy
def ascend_stairs(bot: "Bot") -> bool:
    """
    Navigates to and ascends the nearest upward staircase.
    """
    features = bot.terrain_features[bot.blstats.dungeon_number, bot.blstats.level_number].get("features", {})
    feature = features.get("stairs up", None)

    if feature is not None:
        distances = bot.pathfinder.distances(bot.entity.position)
        closest_feature = min(
            (tuple(f) for f in feature if distances.get(tuple(f))),
            key=lambda f: distances.get(f, np.inf),
            default=None,
        )

        if closest_feature:
            bot.pathfinder.goto(closest_feature)
            bot.step(A.MiscDirection.UP)
            return True

        return False

    else:
        prev_level = bot.blstats.depth
        bot.step(A.MiscDirection.UP)
        curr_level = bot.blstats.depth

        return curr_level < prev_level


@strategy
def goto_room(bot: "Bot") -> bool:
    """
    Moves the agent to the closest room (where distance is calculated as number of agent steps).
    Tips:
    - if we are standing in the room it isn't taken into consideration
    - doors are not treated as part of the room
    - looking at each room consider only closest tile from each room
    """
    return goto_feature_direction(bot, "all", room_detection)


@strategy
def goto_room_west(bot: "Bot") -> bool:
    """
    Similar to `goto_room`, but filters possible rooms westward.
    """
    return goto_feature_direction(bot, "west", room_detection)


@strategy
def goto_room_east(bot: "Bot") -> bool:
    """
    Similar to `goto_room`, but filters possible rooms eastward.
    """
    return goto_feature_direction(bot, "east", room_detection)


@strategy
def goto_room_north(bot: "Bot") -> bool:
    """
    Similar to `goto_room`, but filters possible rooms northward.
    """
    return goto_feature_direction(bot, "north", room_detection)


@strategy
def goto_room_south(bot: "Bot") -> bool:
    """
    Similar to `goto_room`, but filters possible rooms southward.
    """
    return goto_feature_direction(bot, "south", room_detection)


@strategy
def goto_unexplored_room(bot: "Bot") -> bool:
    """
    Similar to `goto_room`, but considers only unexplored rooms (not visited).
    """
    return goto_unexplored_feature(bot, room_detection)


@strategy
def goto_corridor(bot: "Bot") -> bool:
    """
    Moves the agent to the closest corridor (where distance is calculated as number of agent steps).
    Tips:
    - if we are standing in the corridor it isn't taken into consideration
    - doors are treated as part of the corridor
    - looking at each corridor consider only closest tile from each corridor
    - corridors and rooms are labeled using connected components without diagonal connectivity
    """
    return goto_feature_direction(bot, "all", corridor_detection)


@strategy
def goto_corridor_west(bot: "Bot") -> bool:
    """
    Similar to `explore_corridor`, but filters undiscovered tiles westward.
    """
    return goto_feature_direction(bot, "west", corridor_detection)


@strategy
def goto_corridor_east(bot: "Bot") -> bool:
    """
    Similar to `explore_corridor`, but filters undiscovered tiles eastward.
    """
    return goto_feature_direction(bot, "east", corridor_detection)


@strategy
def goto_corridor_north(bot: "Bot") -> bool:
    """
    Similar to `explore_corridor`, but filters undiscovered tiles northward.
    """
    return goto_feature_direction(bot, "north", corridor_detection)


@strategy
def goto_corridor_south(bot: "Bot") -> bool:
    """
    Similar to `explore_corridor`, but filters undiscovered tiles southward.
    """
    return goto_feature_direction(bot, "south", corridor_detection)


@strategy
def goto_unexplored_corridor(bot: "Bot") -> bool:
    """
    Similar to `goto_corridor`, but considers only unexplored corridors (not visited).
    """
    return goto_unexplored_feature(bot, corridor_detection)

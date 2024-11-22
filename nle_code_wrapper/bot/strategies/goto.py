import numpy as np
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import room_detection, save_boolean_array_pillow
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
    stair = utils.isin(bot.glyphs, G.STAIR_DOWN)
    stair_positions = np.argwhere(stair)
    goto_closest(bot, stair_positions)


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
    stair = utils.isin(bot.glyphs, G.STAIR_UP)
    stair_positions = np.argwhere(stair)
    goto_closest(bot, stair_positions)


def goto_closest_corridor(bot: "Bot") -> bool:
    """

    Args:
        bot (Bot): The bot instance that will perform the room navigation.

    Returns:
        bool: True if there is corridor and the bot is directed to it,
              False if there is no corridors.
    """
    corridors = utils.isin(bot.glyphs, frozenset({SS.S_corr, SS.S_litcorr}))
    corridor_positions = np.argwhere(corridors)
    goto_closest(bot, corridor_positions)


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


def goto_closest_room(bot: "Bot") -> bool:
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
    labeled_rooms, num_rooms = room_detection(bot)

    my_position = bot.entity.position
    level = bot.current_level
    unvisited_rooms = []
    # exclude 0 because this is background
    for label in range(1, num_rooms + 1):
        room = labeled_rooms == label
        room = np.logical_and(room, level.walkable)
        # consider rooms which we are not in
        if not label == labeled_rooms[my_position]:
            room_positions = np.argwhere(room)
            distances = np.sum(np.abs(room_positions - my_position), axis=1)
            unvisited_rooms.append((np.min(distances), tuple(room_positions[np.argmin(distances)])))

    closest_position = min(unvisited_rooms, key=lambda x: x[0])[1] if unvisited_rooms else None

    if closest_position:
        bot.pathfinder.goto(closest_position)
        return True
    else:
        return False


def goto_closest_unexplored_room(bot: "Bot") -> bool:
    """
    Directs the bot to the closest unexplored room in the level.

    Args:
        bot (Bot): The bot instance that will perform the room navigation.

    Returns:
        bool: True if an unexplored room is found and the bot is directed to it,
              False if all rooms have been visited.

    Details:
        - Detects and labels different rooms in the level
        - Identifies rooms that haven't been visited yet (no tiles marked as was_on)
        - For each unvisited room, finds the closest position to the bot
        - Directs the bot to the closest position in the nearest unexplored room using pathfinding
        - Background (label 0) is excluded from room consideration
    """
    labeled_rooms, num_rooms = room_detection(bot)

    level = bot.current_level
    unvisited_rooms = []
    # exclude 0 because this is background
    for label in range(1, num_rooms + 1):
        room = labeled_rooms == label
        room = np.logical_and(room, level.walkable)
        # consider only unexplored rooms
        if not np.any(np.logical_and(room, level.was_on)):
            room_positions = np.argwhere(room)
            distances = np.sum(np.abs(room_positions - bot.entity.position), axis=1)
            unvisited_rooms.append((np.min(distances), tuple(room_positions[np.argmin(distances)])))

    closest_position = min(unvisited_rooms, key=lambda x: x[0])[1] if unvisited_rooms else None

    if closest_position:
        bot.pathfinder.goto(closest_position)
        return True
    else:
        return False


# TODO:
# goto closest staricase_down (done)
# goto closest staricase_up (done)
# goto closest room (done)
# goto closest corridor (done)
# goto closest room west
# goto closest room east
# goto closest room south
# goto closest room north
# goto closest corridor west
# goto closest corridor east
# goto closest corridor south
# goto closest corridor north
# goto closest unexplored room (done)

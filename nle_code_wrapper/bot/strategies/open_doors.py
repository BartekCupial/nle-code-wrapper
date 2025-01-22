import numpy as np
from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils


def find_nearest_door(bot: "Bot"):
    closed_doors = np.argwhere(utils.isin(bot.glyphs, G.DOOR_CLOSED))
    neigbors = [bot.pathfinder.reachable(bot.entity.position, tuple(door), adjacent=True) for door in closed_doors]
    distances = bot.pathfinder.distances(bot.entity.position)
    return min(
        ((neighbor, tuple(door)) for neighbor, door in zip(neigbors, closed_doors) if neighbor is not None),
        key=lambda pair: distances.get(pair[0], np.inf),
        default=None,
    )


@strategy
def open_doors(bot: "Bot") -> bool:
    """
    Attempts to open closed doors.
    Tips:
    - prioritizes doors by distance (where distance is calculated as number of agent steps)
    - tries to open the door up to 5 times
    - stop attempts if doors are locked
    """

    adjacent_door = find_nearest_door(bot)
    if adjacent_door:
        bot.pathfinder.goto(adjacent_door[0])

        # open the door multiple times
        doors = utils.isin(bot.glyphs, G.DOOR_CLOSED)
        for _ in range(5):
            # break when we open the doors
            # break if doors are closed
            new_doors = utils.isin(bot.glyphs, G.DOOR_CLOSED)
            if not (doors == new_doors).all() or "door is locked" in bot.message:
                break
            bot.pathfinder.direction(adjacent_door[1])

        return True
    else:
        return False


@strategy
def open_doors_kick(bot: "Bot") -> bool:
    """
    Attempts to open closed doors by kicking them.
    Tips:
    - prioritizes doors by distance (where distance is calculated as number of agent steps)
    - kicks the door up to 5 times
    """

    adjacent_door = find_nearest_door(bot)
    if adjacent_door:
        # kick the door multiple times
        doors = utils.isin(bot.glyphs, G.DOOR_CLOSED)
        for _ in range(5):
            bot.pathfinder.goto(adjacent_door[0])
            # break when we break the doors
            # break when we injure our leg
            new_doors = utils.isin(bot.glyphs, G.DOOR_CLOSED)
            if not (doors == new_doors).all() or "no shape for kicking" in bot.message:
                break
            bot.step(A.Command.KICK)
            bot.pathfinder.direction(adjacent_door[1])

        return True
    else:
        return False


@strategy
def open_doors_key(bot: "Bot") -> bool:
    """
    Attempts to open closed doors with key.
    Tips:
    - prioritizes doors by distance (where distance is calculated as number of agent steps)
    - needs a key to open the doors
    - if no key, nothing happens
    """
    key_letter = None
    for tool in bot.inventory["tools"]:
        if tool.is_key:
            key_letter = tool.letter
            break

    if key_letter is None:
        return False

    adjacent_door = find_nearest_door(bot)
    if adjacent_door:
        old_opened_doors = utils.isin(bot.glyphs, G.DOOR_OPENED)
        bot.pathfinder.goto(adjacent_door[0])
        bot.step(A.Command.APPLY)
        if "What do you want to use or apply?" in bot.message:
            bot.step(key_letter)

            if "In what direction?" in bot.message:
                bot.pathfinder.direction(adjacent_door[1])

                if "Unlock it?" in bot.message:
                    bot.type_text("y")
                    bot.pathfinder.direction(adjacent_door[1])

        # return True if we opened the door
        opened_doors = utils.isin(bot.glyphs, G.DOOR_OPENED)
        return not (old_opened_doors == opened_doors).all()
    else:
        return False

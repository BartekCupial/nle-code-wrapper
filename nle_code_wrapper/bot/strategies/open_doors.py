import numpy as np
from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils


@strategy
def open_doors(bot: "Bot") -> bool:
    """
    Attempts to open the nearest reachable closed door for the given bot.
    This function identifies all closed doors on the current level and determines
    the nearest one that the bot can reach. If a reachable closed door is found,
    the bot will move to an adjacent position and attempt to open the door.
    Args:
        bot (Bot): The bot instance attempting to open doors.
    Returns:
        bool: True if a reachable closed door was found and the bot attempted to open it,
              False if no reachable closed doors were found.
    """

    closed_doors = np.argwhere(utils.isin(bot.glyphs, G.DOOR_CLOSED))

    reachable_door = min(
        (tuple(door) for door in closed_doors if bot.pathfinder.reachable_adjacent(bot.entity.position, tuple(door))),
        key=lambda door: bot.pathfinder.distance(bot.entity.position, door),
        default=None,
    )

    if reachable_door:
        adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, reachable_door)
        bot.pathfinder.goto(adjacent)

        # open the door multiple times
        doors = utils.isin(bot.glyphs, G.DOOR_CLOSED)
        for _ in range(5):
            # break when we open the doors
            # break if doors are closed
            new_doors = utils.isin(bot.glyphs, G.DOOR_CLOSED)
            if not (doors == new_doors).all() or "door is locked" in bot.message:
                break
            bot.pathfinder.direction(reachable_door)

        return True
    else:
        return False


@strategy
def open_doors_kick(bot: "Bot") -> bool:
    """
    Attempts to open closed doors by kicking them if they are reachable.
    This function finds the nearest closed door that is reachable from the bot's current position.
    If such a door is found, the bot moves to an adjacent position, kicks the door, and then
    determines the direction of the door to complete the action.
    Args:
        bot (Bot): The bot instance that will perform the action.
    Returns:
        bool: True if a reachable closed door was found and kicked, False otherwise.
    """

    closed_doors = np.argwhere(utils.isin(bot.glyphs, G.DOOR_CLOSED))

    reachable_door = min(
        (tuple(door) for door in closed_doors if bot.pathfinder.reachable_adjacent(bot.entity.position, tuple(door))),
        key=lambda door: bot.pathfinder.distance(bot.entity.position, door),
        default=None,
    )

    if reachable_door:
        adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, reachable_door)
        bot.pathfinder.goto(adjacent)

        # kick the door multiple times
        doors = utils.isin(bot.glyphs, G.DOOR_CLOSED)
        for _ in range(5):
            # break when we break the doors
            # break when we injure our leg
            new_doors = utils.isin(bot.glyphs, G.DOOR_CLOSED)
            if not (doors == new_doors).all() or "no shape for kicking" in bot.message:
                break
            bot.step(A.Command.KICK)
            bot.pathfinder.direction(reachable_door)

        return True
    else:
        return False


@strategy
def open_doors_key(bot: "Bot") -> bool:
    """
    Attempts to open closed doors by using a key if one is available.

    Args:
        bot (Bot): The bot instance that will perform the action.
    Returns:
        bool: True if a reachable closed door was found and attempted to be opened with a key, False otherwise.
    """
    closed_doors = np.argwhere(utils.isin(bot.glyphs, G.DOOR_CLOSED))

    reachable_door = min(
        (tuple(door) for door in closed_doors if bot.pathfinder.reachable_adjacent(bot.entity.position, tuple(door))),
        key=lambda door: bot.pathfinder.distance(bot.entity.position, door),
        default=None,
    )

    if reachable_door:
        old_opened_doors = utils.isin(bot.glyphs, G.DOOR_OPENED)
        adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, reachable_door)
        bot.pathfinder.goto(adjacent)
        bot.step(A.Command.APPLY)
        if "What do you want to use or apply?" in bot.message:
            for tool in bot.inventory["tools"]:
                if tool.is_key:
                    bot.step(tool.letter)
                    break

            if "In what direction?" in bot.message:
                bot.pathfinder.direction(reachable_door)

                if "Unlock it?" in bot.message:
                    bot.type_text("y")
                    bot.pathfinder.direction(reachable_door)

        # return True if we opened the door
        opened_doors = utils.isin(bot.glyphs, G.DOOR_OPENED)
        return not (old_opened_doors == opened_doors).all()
    else:
        return False

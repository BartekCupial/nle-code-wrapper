from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot


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

    level = bot.current_level()
    closed_doors = level.object_coords(G.DOOR_CLOSED)

    reachable_door = min(
        (door for door in closed_doors if bot.pathfinder.reachable_adjacent(bot.entity.position, door)),
        key=lambda door: bot.pathfinder.distance(bot.entity.position, door),
        default=None,
    )

    if reachable_door:
        adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, reachable_door)
        bot.pathfinder.goto(adjacent)
        bot.pathfinder.direction(reachable_door)

        return True
    else:
        return False


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

    level = bot.current_level()
    closed_doors = level.object_coords(G.DOOR_CLOSED)

    reachable_door = min(
        (door for door in closed_doors if bot.pathfinder.reachable_adjacent(bot.entity.position, door)),
        key=lambda door: bot.pathfinder.distance(bot.entity.position, door),
        default=None,
    )

    if reachable_door:
        adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, reachable_door)
        bot.pathfinder.goto(adjacent)
        bot.step(A.Command.KICK)
        bot.pathfinder.direction(reachable_door)

        return True
    else:
        return False


def open_doors_key(bot: "Bot") -> bool:
    """
    Attempts to open closed doors by using a key if one is available.

    Args:
        bot (Bot): The bot instance that will perform the action.
    Yields:
        bool: True if a reachable closed door was found and attempted to be opened with a key, False otherwise.
    """
    level = bot.current_level()
    closed_doors = level.object_coords(G.DOOR_CLOSED)

    reachable_door = min(
        (door for door in closed_doors if bot.pathfinder.reachable_adjacent(bot.entity.position, door)),
        key=lambda door: bot.pathfinder.distance(bot.entity.position, door),
        default=None,
    )

    if reachable_door:
        adjacent = bot.pathfinder.reachable_adjacent(bot.entity.position, reachable_door)
        bot.pathfinder.goto(adjacent)
        bot.step(A.Command.APPLY)

        return True
    else:
        return False

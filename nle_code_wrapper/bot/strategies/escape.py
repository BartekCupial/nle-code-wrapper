from typing import List, Optional, Tuple

import numpy as np
from nle.nethack import actions as A

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import EnemyAppeared, LostHP
from nle_code_wrapper.bot.inventory.properties import ItemBeatitude
from nle_code_wrapper.bot.strategy import repeat, strategy
from nle_code_wrapper.utils.strategies import room_detection


def escape_to_location(bot, target_location: Tuple[int, int]) -> bool:
    """
    Moves step-by-step to a target location, re-evaluating the path at each step
    to avoid dynamic obstacles like monsters. This is a safer way to travel
    when enemies are nearby.

    Returns:
        bool: True if the location was reached, False otherwise.
    """

    # Loop until the bot reaches the target position.
    while bot.entity.position != target_location:
        try:
            path = bot.pathfinder.get_path_to(target_location)

            # If no path exists, the way is blocked.
            if not path or len(path) <= 1:
                bot.add_message("Path is blocked, cannot escape.")
                return False

            # Take a single step along the newly calculated path.
            bot.pathfinder.move(path[1])

            # Check for game interruptions (e.g., a prompt)
            if bot.in_yn_function or bot.in_getlin:
                bot.add_message("Escape interrupted by game prompt.")
                return False

        except (LostHP, EnemyAppeared):
            # If the bot loses HP or an enemy appears, re-evaluate the path.
            continue

    return False


@strategy
def escape_upstairs(bot: "Bot") -> bool:
    """
    Attempts to escape upstairs. Similar to `ascend_stairs`, but will try to avoid monsters when escaping.
    """
    features = bot.terrain_features[bot.blstats.dungeon_number, bot.blstats.level_number].get("features", {})
    feature = features.get("stairs up", None)

    if feature is not None:
        distances = bot.pathfinder.distances(bot.entity.position)
        closest_feature = min(
            (tuple(f) for f in feature if distances.get(tuple(f)) is not None),
            key=lambda f: distances.get(f, np.inf),
            default=None,
        )

        if closest_feature:
            escape_to_location(bot, closest_feature)
            bot.step(A.MiscDirection.UP)
            return True

    return False


@strategy
def escape_downstairs(bot: "Bot") -> bool:
    """
    Attempts to escape downstairs. Similar to `descend_stairs`, but will try to avoid monsters when escaping.
    """
    features = bot.terrain_features[bot.blstats.dungeon_number, bot.blstats.level_number].get("features", {})
    feature = features.get("stairs down", None)

    if feature is not None:
        distances = bot.pathfinder.distances(bot.entity.position)
        closest_feature = min(
            (tuple(f) for f in feature if distances.get(tuple(f)) is not None),
            key=lambda f: distances.get(f, np.inf),
            default=None,
        )

        if closest_feature:
            escape_to_location(bot, closest_feature)
            bot.step(A.MiscDirection.DOWN)
            return True

    return False


@strategy
def escape_room(bot: "Bot") -> bool:
    """
    Attempts to escape to a room. Similar to `goto_room`, but will try to avoid monsters when escaping.
    """
    room_labels, num_rooms = room_detection(bot)

    # since the monster cost is pretty high we will always pick the safest room by default
    room_coords = np.argwhere(room_labels)
    distances = bot.pathfinder.distances(bot.entity.position)

    closest_room = min(
        (tuple(coord) for coord in room_coords if distances.get(tuple(coord)) is not None),
        key=lambda coord: distances.get(tuple(coord), np.inf),
        default=None,
    )

    if closest_room:
        escape_to_location(bot, closest_room)
        bot.pathfinder.goto(closest_room)
        return True

    # If no safe room is found, consider other escape options.
    # For example, moving towards the known safe corridor.
    # This part can be expanded based on the bot's knowledge and environment.
    return False

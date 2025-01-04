from functools import wraps

import numpy as np
from nle_utils.glyph import G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.exceptions import BotFinished, BotPanic
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import label_dungeon_features, save_boolean_array_pillow


def strategy(func):
    """
    A decorator that increments the bot's strategy_step attribute before executing the function.

    Args:
        func: The function to be decorated

    Returns:
        wrapper: The wrapped function that increments strategy_step before execution
    """

    @wraps(func)
    def wrapper(bot: "Bot", *args, **kwargs):
        bot.strategy_steps += 1

        if bot.strategy_steps >= bot.max_strategy_steps:
            bot.truncated = True
            raise BotFinished

        return func(bot, *args, **kwargs)

    return wrapper


def repeat(func):
    """
    A decorator that repeatedly executes the given function until a BotFinished exception is raised.
    Args:
        func (callable): The function to be repeatedly executed. It should accept a "Bot" instance as its first argument.
    Returns:
        callable: A wrapper function that executes the given function in a loop until a BotFinished exception is encountered.
    """

    @wraps(func)
    def wrapper(bot: "Bot", *args, **kwargs):
        while func(bot, *args, **kwargs):
            pass

    return wrapper


def repeat_n_times(n: int):
    def decorator(func):
        @wraps(func)
        def wrapper(bot: "Bot", *args, **kwargs):
            i = 0
            while func(bot, *args, **kwargs) and i < n:
                i += 1

        return wrapper

    return decorator


def repeat_until_discovery(func):
    @wraps(func)
    def wrapper(bot: "Bot", *args, **kwargs):
        def get_labels(features):
            """
            return labels of dungeon part where we are
            """
            labels, num_labels = ndimage.label(features > 0)
            current_label = labels == labels[bot.entity.position]
            return set(np.unique(features[current_label]))

        def get_doors():
            """
            return positions of the closed doors in the dungeon
            """
            return set(map(tuple, np.argwhere(utils.isin(bot.glyphs, G.DOOR_CLOSED))))

        def get_dead_ends(features):
            """
            return positions of the dead ends in the dungeon
            dead end is a position which has on or less cardinal neighbors
            to confirm dead end we check if bot was on this position
            """
            dead_ends = np.array(
                [
                    n
                    for n in np.argwhere(features)
                    if bot.current_level.was_on[tuple(n)]
                    and len(bot.pathfinder.neighbors(tuple(n), cardinal_only=True)) <= 1
                ]
            )
            return set(map(tuple, dead_ends))

        def get_items():
            """
            return positions of the items in the dungeon
            """
            return set(map(tuple, np.argwhere(utils.isin(bot.glyphs, G.ITEMS))))

        features, num_rooms, num_corridors = label_dungeon_features(bot)
        labels = get_labels(features)
        doors = get_doors()
        dead_ends = get_dead_ends(features)
        items = get_items()
        seen = bot.current_level.seen.copy()

        while func(bot, *args, **kwargs):
            new_seen = np.logical_and(np.logical_not(seen), bot.current_level.seen)
            new_seen = set(map(tuple, np.argwhere(new_seen)))

            # 1) if we have new room of new corridor break
            new_features, new_num_rooms, new_num_corridors = label_dungeon_features(bot)
            new_labels = get_labels(new_features)
            if len(labels) < len(new_labels):
                return

            # 2) if we have new door break
            new_doors = get_doors()
            for door in new_doors.difference(doors).intersection(new_seen):
                if bot.pathfinder.reachable_adjacent(bot.entity.position, door):
                    return

            # 3) if we have dead new end break
            new_dead_ends = get_dead_ends(new_features)
            if new_dead_ends.difference(dead_ends):
                return

            # 4) if we have new item break
            new_items = get_items()
            for item in new_items.difference(items).intersection(new_seen):
                if bot.pathfinder.get_path_to(item):
                    return

            seen = bot.current_level.seen.copy()

    return wrapper

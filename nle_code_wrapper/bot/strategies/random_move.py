import numpy as np

from nle_code_wrapper.bot import Bot


def random_move(bot: "Bot") -> bool:
    """
    Randomly move to a neighbor position.

    Args:
        bot (Bot): The bot instance.
    Returns:
        bool: True.
    """
    neighbors = bot.pathfinder.neighbors(bot.entity.position)
    goal = neighbors[np.random.choice(len(neighbors))]
    bot.pathfinder.goto(goal)
    return True

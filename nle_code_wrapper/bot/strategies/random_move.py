import numpy as np

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def random_move(bot: "Bot") -> bool:
    """
    Randomly move to a neighbor position.
    """
    neighbors = bot.pathfinder.neighbors(bot.entity.position)

    if len(neighbors) == 0:
        return False

    goal = neighbors[np.random.choice(len(neighbors))]
    bot.pathfinder.goto(goal)
    return True

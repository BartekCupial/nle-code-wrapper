import numpy as np

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import Strategy


@Strategy.wrap
def random_move(bot: "Bot"):
    neighbors = bot.pathfinder.neighbors(bot.entity.position)
    goal = neighbors[np.random.choice(len(neighbors))]
    bot.pathfinder.goto(goal)
    yield True

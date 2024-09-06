import numpy as np

from nle_code_wrapper.bot import Bot


def random_move(bot: "Bot"):
    neighbors = bot.pathfinder.movements.get_neighbors(bot.entity.position)
    goal = neighbors[np.random.choice(len(neighbors))]
    bot.pathfinder.goto(goal)
    yield

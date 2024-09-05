from typing import TYPE_CHECKING

import numpy as np

from nle_code_wrapper.plugins.pathfinder.chebyshev_search import ChebyshevSearch
from nle_code_wrapper.plugins.pathfinder.distance import chebyshev_distance
from nle_code_wrapper.plugins.pathfinder.goto import calc_direction, direction, goto, move
from nle_code_wrapper.plugins.pathfinder.movements import Movements

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


class Pathfinder:
    def __init__(self, bot: "Bot"):
        self.bot: Bot = bot
        self.movements: Movements = Movements(bot)
        self.search = ChebyshevSearch(self.movements)

    def astar(self, start, goal):
        return self.search.astar(start, goal)

    def distances(self, start):
        return self.search.distances(start)

    def get_path_to(self, goal):
        result = self.get_path_from_to(self.bot.position, goal)
        return result

    def get_path_from_to(self, start, goal):
        result = self.search.astar(start, goal)
        return result

    def goto(self, goal):
        return goto(self.bot, goal)

    def move(self, pos):
        return move(self.bot, pos[0], pos[1])

    def direction(self, pos):
        bot_pos = self.bot.entity.position
        dir = calc_direction(bot_pos[0], bot_pos[1], pos[0], pos[1])
        return direction(self.bot, dir)

    def distance(self, n1, n2):
        return chebyshev_distance(n1, n2)

    def reachable_adjacent(self, start, goal):
        distances = self.distances(start)
        neighbors = self.movements.get_neighbors(goal)

        n_dist = []
        for n in neighbors:
            if n in distances:
                n_dist.append(distances[n])

        if len(n_dist) == 0:
            return False

        idx = np.argmin(n_dist)
        return neighbors[idx]

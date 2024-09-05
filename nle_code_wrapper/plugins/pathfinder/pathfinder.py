from typing import TYPE_CHECKING

from nle_code_wrapper.plugins.pathfinder.chebyshev_search import ChebyshevSearch
from nle_code_wrapper.plugins.pathfinder.distance import chebyshev_distance
from nle_code_wrapper.plugins.pathfinder.goto import goto
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

    def distance(self, n1, n2):
        return chebyshev_distance(n1, n2)

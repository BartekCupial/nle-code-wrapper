from nle_code_wrapper.bot.pathfinder.distance import chebyshev_distance
from nle_code_wrapper.bot.pathfinder.movements import Movements
from nle_code_wrapper.bot.pathfinder.search_algorithm import SearchAlgorithm


class ChebyshevSearch(SearchAlgorithm):
    """sample use of the search algorithm. In this exemple we work on a maze made of ascii characters,
    and a 'node' is just a (x,y) tuple that represents a reachable position"""

    def __init__(self, movements: Movements):
        self.movements: Movements = movements

    def heuristic_cost_estimate(self, n1, n2):
        """computes the Chabyshev distance between two (x,y) tuples"""
        return chebyshev_distance(n1, n2)

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return 1

    def neighbors(self, node):
        return self.movements.neighbors(node)

from typing import List, Tuple

from numpy import int64

from nle_code_wrapper.bot.pathfinder.distance import chebyshev_distance
from nle_code_wrapper.bot.pathfinder.movements import Movements
from nle_code_wrapper.bot.pathfinder.search_algorithm import SearchAlgorithm


class ChebyshevSearch(SearchAlgorithm):
    """Sample use of the search algorithm. In this exemple we work on a maze made of ascii characters,
    and a 'node' is just a (x,y) tuple that represents a reachable position"""

    def __init__(self, movements: Movements) -> None:
        self.movements: Movements = movements

    def heuristic_cost_estimate(self, n1: Tuple[int64, int64], n2: Tuple[int64, int64]) -> int64:
        """computes the Chabyshev distance between two (x,y) tuples

        Args:
            n1 (Tuple[int64, int64]): first node
            n2 (Tuple[int64, int64]): second node

        Returns:
            int64: Chebyshev distance between n1 and n2
        """
        return chebyshev_distance(n1, n2)

    def distance_between(self, n1: Tuple[int64, int64], n2: Tuple[int64, int64]) -> int:
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return 1

    def neighbors(self, node: Tuple[int64, int64]) -> List[Tuple[int64, int64]]:
        return self.movements.neighbors(node)

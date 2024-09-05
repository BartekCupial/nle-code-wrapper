from nle_code_wrapper.plugins.pathfinder.astar import AStar
from nle_code_wrapper.plugins.pathfinder.distance import chebyshev_distance


class ChebyshevAStar(AStar):
    """sample use of the astar algorithm. In this exemple we work on a maze made of ascii characters,
    and a 'node' is just a (x,y) tuple that represents a reachable position"""

    def __init__(self, movements):
        self.movements = movements

    def heuristic_cost_estimate(self, n1, n2):
        """computes the Chabyshev distance between two (x,y) tuples"""
        return chebyshev_distance(n1, n2)

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return 1

    def neighbors(self, node):
        return self.movements.get_neighbors(node)

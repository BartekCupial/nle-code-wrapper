from nle_code_wrapper.plugins.pathfinder.astar import ChebyshevAStar
from nle_code_wrapper.plugins.pathfinder.distance import chebyshev_distance
from nle_code_wrapper.plugins.pathfinder.goto import goto
from nle_code_wrapper.plugins.pathfinder.movements import Movements


class Pathfinder:
    def __init__(self, bot):
        self.bot = bot
        self.state_movements = Movements(bot)
        self.state_goal = None
        self.astar_context = None
        self.astart_timedout = False
        self.dynamic_goal = False
        self.path = []
        self.path_updated = False
        self.digging = False
        self.placing = False
        self.placing_block = None

    def get_path_to(self, movements, goal):
        result = self.get_path_from_to(movements, self.bot.position, goal)
        return result

    def get_path_from_to(self, movements, start, goal):
        astar = ChebyshevAStar(movements)
        result = astar.astar(start, goal)
        return result

    def goto(self, goal):
        return goto(self.bot, goal)

    def distance(self, n1, n2):
        return chebyshev_distance(n1, n2)

from typing import TYPE_CHECKING

import numpy as np
from nle.nethack import actions as A

from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.pathfinder.chebyshev_search import ChebyshevSearch
from nle_code_wrapper.bot.pathfinder.distance import chebyshev_distance
from nle_code_wrapper.bot.pathfinder.movements import Movements

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


def calc_direction(from_y, from_x, to_y, to_x):
    assert abs(from_y - to_y) <= 1 and abs(from_x - to_x) <= 1, ((from_y, from_x), (to_y, to_x))

    ret = ""
    if to_y == from_y + 1:
        ret += "s"
    if to_y == from_y - 1:
        ret += "n"
    if to_x == from_x + 1:
        ret += "e"
    if to_x == from_x - 1:
        ret += "w"
    if ret == "":
        ret = "."

    return ret


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
        result = self.get_path_from_to(self.bot.entity.position, goal)
        return result

    def get_path_from_to(self, start, goal):
        result = self.search.astar(start, goal)
        return result

    def direction(self, pos):
        bot_pos = self.bot.entity.position
        dir = calc_direction(bot_pos[0], bot_pos[1], pos[0], pos[1])

        action = {
            "n": A.CompassDirection.N,
            "s": A.CompassDirection.S,
            "e": A.CompassDirection.E,
            "w": A.CompassDirection.W,
            "ne": A.CompassDirection.NE,
            "se": A.CompassDirection.SE,
            "nw": A.CompassDirection.NW,
            "sw": A.CompassDirection.SW,
            ">": A.MiscDirection.DOWN,
            "<": A.MiscDirection.UP,
            ".": A.MiscDirection.WAIT,
        }[dir]

        self.bot.step(action)

    def move(self, dir):
        self.direction(dir)

        if self.bot.entity.position != dir:
            raise BotPanic(
                f'agent position do not match after "move": '
                f"expected ({dir[0]}, {dir[1]}), got ({self.bot.entity.position[0]}, {self.bot.entity.position[1]})"
            )

    def goto(self, goal, fast=False):
        cont = True
        while cont and self.bot.entity.position != goal:
            path = self.get_path_to(goal)
            if path is None:
                raise BotPanic("end point is no longer accessible")
            orig_path = list(path)
            path = orig_path[1:]

            # TODO: implement fast_goto
            # if fast and len(path) > 2:
            #     my_position = bot.entity.position
            #     bot.pathfinder.fast_go_to()

            for point in path:
                # TODO: check if there is peaceful monster
                if not self.bot.current_level().walkable[point]:
                    cont = True
                    break
                self.move(point)
            else:
                cont = False

        return True

    def distance(self, n1, n2):
        return chebyshev_distance(n1, n2)

    def neighbors(self, pos):
        return self.movements.neighbors(pos)

    def reachable_adjacent(self, start, goal):
        distances = self.distances(start)
        neighbors = self.neighbors(goal)

        n_dist = []
        for n in neighbors:
            if n in distances:
                n_dist.append(distances[n])

        if len(n_dist) == 0:
            return False

        idx = np.argmin(n_dist)
        return neighbors[idx]

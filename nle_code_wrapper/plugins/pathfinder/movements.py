from dataclasses import dataclass
from types import SimpleNamespace

from astar import SearchNode
from nle_utils.glyph import C, G

from nle_code_wrapper.utils import utils

cardinal_directions = [
    SimpleNamespace(x=-1, y=0),
    SimpleNamespace(x=1, y=0),
    SimpleNamespace(x=0, y=-1),
    SimpleNamespace(x=0, y=1),
]

intermediate_directions = [
    SimpleNamespace(x=-1, y=-1),
    SimpleNamespace(x=-1, y=1),
    SimpleNamespace(x=1, y=-1),
    SimpleNamespace(x=1, y=1),
]


class Movements:
    def __init__(self, bot):
        self.bot = bot

    def get_glyph(self, pos, dx, dy):
        x = pos[0] + dx
        y = pos[1] + dy
        if 0 <= x < C.SIZE_Y and 0 <= y < C.SIZE_X:
            return self.bot.glyphs[(x, y)], (x, y)
        else:
            return None, (x, y)

    def get_move_forward(self, node, dir, neighbors):
        glyph, pos = self.get_glyph(node, dir.x, dir.y)

        # out of bounds
        if glyph is None:
            return

        # check if not walkable
        if glyph in frozenset.union(G.WALL, G.STONE, G.STONE):
            return

        neighbors.append(pos)

    def get_neighbors(self, node):
        neighbors = []

        for dir in cardinal_directions + intermediate_directions:
            self.get_move_forward(node, dir, neighbors)
            # if self.allowParkour:
            #     self.getMoveParkourForward(node, dir, neighbors)

        # self.getMoveDown(node, neighbors)
        # self.getMoveUp(node, neighbors)

        return neighbors

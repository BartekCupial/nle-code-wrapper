from typing import TYPE_CHECKING

from nle_utils.glyph import C, G

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot

cardinal_directions = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
]

intermediate_directions = [
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),
]


class Movements:
    def __init__(self, bot: "Bot", allow_walking_through_traps=True):
        self.bot: "Bot" = bot
        self.allow_walking_through_traps = allow_walking_through_traps

    def walkable(self, pos):
        level = self.bot.current_level()
        walkable = level.walkable[pos] and not (level.objects[pos] in G.BOULDER)
        return walkable

    def get_move_forward(self, pos, dir, neighbors):
        new_pos = (pos[0] + dir[0], pos[1] + dir[1])

        # out of bounds
        if not (0 <= new_pos[0] < C.SIZE_Y and 0 <= new_pos[1] < C.SIZE_X):
            return

        # check if not walkable
        if self.walkable(new_pos):
            neighbors.append(new_pos)

    def get_neighbors(self, node):
        neighbors = []

        for dir in cardinal_directions + intermediate_directions:
            self.get_move_forward(node, dir, neighbors)

        return neighbors

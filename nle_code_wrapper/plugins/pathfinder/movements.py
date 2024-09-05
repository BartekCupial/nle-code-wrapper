from typing import TYPE_CHECKING

from nle_utils.glyph import C, G
from nle_utils.level import Level as DungeonLevel

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

    @property
    def walkable_diagonally(self):
        level = self.bot.current_level()
        return level.dungeon_number != DungeonLevel.SOKOBAN

    def walkable_cardinal(self, pos):
        level = self.bot.current_level()
        walkable = level.walkable[pos] and not (level.objects[pos] in G.BOULDER)
        return walkable

    def get_move_cardinal(self, pos, dir, neighbors):
        new_pos = (pos[0] + dir[0], pos[1] + dir[1])

        # out of bounds
        if not (0 <= new_pos[0] < C.SIZE_Y and 0 <= new_pos[1] < C.SIZE_X):
            return

        # check if not walkable
        if self.walkable_cardinal(new_pos):
            neighbors.append(new_pos)

    def walkable_intermediate(self, pos, new_pos):
        level = self.bot.current_level()
        # we restrict diagonal movements in the doors
        # TODO: handle moving diagonally when heavy
        # the character can only move diagonally if his or her total inventory weight is 600 or less.
        # Otherwise, "You are carrying too much to get through."
        walkable = (
            level.walkable[new_pos]
            and not level.objects[new_pos] in frozenset.union(G.BOULDER, G.DOOR_OPENED)
            and not level.objects[pos] in G.DOOR_OPENED
        )
        return walkable

    def get_move_intermediate(self, pos, dir, neighbors):
        new_pos = (pos[0] + dir[0], pos[1] + dir[1])

        # out of bounds
        if not (0 <= new_pos[0] < C.SIZE_Y and 0 <= new_pos[1] < C.SIZE_X):
            return

        # check if not walkable
        if self.walkable_intermediate(pos, new_pos):
            neighbors.append(new_pos)

    def get_neighbors(self, node):
        neighbors = []

        for dir in cardinal_directions:
            self.get_move_cardinal(node, dir, neighbors)

        if self.walkable_diagonally:
            for dir in intermediate_directions:
                self.get_move_intermediate(node, dir, neighbors)

        return neighbors

from typing import TYPE_CHECKING, Any, List, Tuple, Union

from nle_utils.glyph import C, G
from nle_utils.level import Level as DungeonLevel
from numpy import bool_, int64

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
    def __init__(self, bot: "Bot", allow_walking_through_traps: bool = True) -> None:
        self.bot: "Bot" = bot
        self.allow_walking_through_traps = allow_walking_through_traps

    @property
    def walkable_diagonally(self) -> bool_:
        level = self.bot.current_level()
        return level.dungeon_number != DungeonLevel.SOKOBAN

    def walkable_cardinal(self, pos: Tuple[int64, int64]) -> Union[bool_, bool]:
        level = self.bot.current_level()
        walkable = level.walkable[pos] and not (level.objects[pos] in G.BOULDER)
        return walkable

    def get_move_cardinal(
        self, pos: Tuple[int64, int64], dir: Tuple[int, int], neighbors: List[Union[Any, Tuple[int64, int64]]]
    ) -> None:
        new_pos = (pos[0] + dir[0], pos[1] + dir[1])

        # out of bounds
        if not (0 <= new_pos[0] < C.SIZE_Y and 0 <= new_pos[1] < C.SIZE_X):
            return

        # check if not walkable
        if self.walkable_cardinal(new_pos):
            neighbors.append(new_pos)

    def walkable_intermediate(self, pos: Tuple[int64, int64], new_pos: Tuple[int64, int64]) -> Union[bool_, bool]:
        level = self.bot.current_level()
        # we restrict diagonal movements in the doors
        # TODO: handle moving diagonally when heavy
        # the character can only move diagonally if his or her total inventory weight is 600 or less.
        # Otherwise, "You are carrying too much to get through."
        walkable = (
            # can we walk there
            level.walkable[new_pos]
            # cannot move diagonally throught doors and boulders
            and not level.objects[new_pos] in frozenset.union(G.BOULDER, G.DOOR_OPENED)
            and not level.objects[pos] in frozenset.union(G.BOULDER, G.DOOR_OPENED)
            and not level.doors[new_pos]
            and not level.doors[pos]
        )
        return walkable

    def get_move_intermediate(
        self, pos: Tuple[int64, int64], dir: Tuple[int, int], neighbors: List[Union[Any, Tuple[int64, int64]]]
    ) -> None:
        new_pos = (pos[0] + dir[0], pos[1] + dir[1])

        # out of bounds
        if not (0 <= new_pos[0] < C.SIZE_Y and 0 <= new_pos[1] < C.SIZE_X):
            return

        # check if not walkable
        if self.walkable_intermediate(pos, new_pos):
            neighbors.append(new_pos)

    def neighbors(self, node: Tuple[int64, int64]) -> List[Union[Any, Tuple[int64, int64]]]:
        neighbors = []

        for dir in cardinal_directions:
            self.get_move_cardinal(node, dir, neighbors)

        if self.walkable_diagonally:
            for dir in intermediate_directions:
                self.get_move_intermediate(node, dir, neighbors)

        return neighbors

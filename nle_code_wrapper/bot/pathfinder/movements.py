from typing import TYPE_CHECKING, Any, List, Tuple, Union

from nle import nethack
from nle_utils.glyph import SS, C, G
from nle_utils.level import Level as DungeonLevel
from numpy import int64

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
    """
    This class is responsible for calculating the possible movements of the player.  It is used by the Bot class to calculate the possible moves.

    The player can move in 4 cardinal directions (up, down, left, right) and in 4 intermediate directions (up-left, up-right, down-left, down-right).
    The player can move diagonally in all levels except for Sokoban levels.  The player can walk on every tile in the level, except for boulders, doors, walls, and traps.
    The player can walk diagonally through doors and boulders, but not through traps.

    The player can only move diagonally if his or her total inventory weight is 600 or less.  Otherwise, the player will receive the message "You are carrying too much to get through."
    """

    def __init__(
        self,
        bot: "Bot",
        allow_walking_through_traps: bool = True,
        levitating: bool = False,
        monster_collision: bool = True,
        cardinal_only: bool = False,
    ) -> None:
        self.bot: "Bot" = bot
        self.allow_walking_through_traps = allow_walking_through_traps  # TODO: handle traps
        self.levitating = levitating
        self.monster_collision = monster_collision
        self.cardinal_only = cardinal_only

    @property
    def walkable_diagonally(self) -> bool:
        level = self.bot.current_level
        return level.dungeon_number != DungeonLevel.SOKOBAN.value

    def walkable_cardinal(self, pos: Tuple[int64, int64], new_pos: Tuple[int64, int64]) -> bool:
        level = self.bot.current_level
        glyph_walkable = level.walkable[new_pos]

        if self.levitating and level.objects[new_pos] in frozenset.union(frozenset({SS.S_lava, SS.S_water}), G.BOULDER):
            glyph_walkable = True

        if self.monster_collision:
            glyph_walkable = glyph_walkable and new_pos not in [e.position for e in self.bot.entities]

        return glyph_walkable

    def get_move_cardinal(
        self, pos: Tuple[int64, int64], dir: Tuple[int, int], neighbors: List[Union[Any, Tuple[int64, int64]]]
    ) -> None:
        """
        This method checks if the player can move in a cardinal direction.  If the player can move, then the new position is appended to the neighbors list.

        Args:
            pos (Tuple[int64, int64]): The current position of the player.
            dir (Tuple[int, int]): The direction in which the player is trying to move.
            neighbors (List[Union[Any, Tuple[int64, int64]]]): A list of possible moves for the player.
        """
        new_pos = (pos[0] + dir[0], pos[1] + dir[1])

        # out of bounds
        if not (0 <= new_pos[0] < C.SIZE_Y and 0 <= new_pos[1] < C.SIZE_X):
            return

        # check if not walkable
        if self.walkable_cardinal(pos, new_pos):
            neighbors.append(new_pos)

    def walkable_intermediate(self, pos: Tuple[int64, int64], new_pos: Tuple[int64, int64]) -> bool:
        """
        This method checks if the player can move in an intermediate direction.

        Args:
            pos (Tuple[int64, int64]): The current position of the player.
            new_pos (Tuple[int64, int64]): The position the player is trying to move to.

        Returns:
            bool: True if the player can move to the new position, False otherwise
        """
        level = self.bot.current_level
        # we restrict diagonal movements in the doors
        # TODO: handle moving diagonally when heavy
        # the character can only move diagonally if his or her total inventory weight is 600 or less.
        # Otherwise, "You are carrying too much to get through."
        glyph_walkable = level.walkable[new_pos]

        if self.levitating and level.objects[new_pos] in frozenset.union(frozenset({SS.S_lava, SS.S_water}), G.BOULDER):
            glyph_walkable = True

        if self.monster_collision:
            glyph_walkable = glyph_walkable and new_pos not in [e.position for e in self.bot.entities]

        walkable = (
            # can we walk there
            glyph_walkable
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
        """
        This method checks if the player can move in an intermediate direction.  If the player can move, then the new position is appended to the neighbors list.

        Args:
            pos (Tuple[int64, int64]): The current position of the player.
            dir (Tuple[int, int]): The direction in which the player is trying to move.
            neighbors (List[Union[Any, Tuple[int64, int64]]]): A list of possible moves for the player
        """
        new_pos = (pos[0] + dir[0], pos[1] + dir[1])

        # out of bounds
        if not (0 <= new_pos[0] < C.SIZE_Y and 0 <= new_pos[1] < C.SIZE_X):
            return

        # check if not walkable
        if self.walkable_intermediate(pos, new_pos):
            neighbors.append(new_pos)

    def neighbors(self, node: Tuple[int64, int64]) -> List[Union[Any, Tuple[int64, int64]]]:
        """
        This method calculates the possible moves for the player.

        Args:
            node (Tuple[int64, int64]): The current position of the player.
        Returns:
            List[Union[Any, Tuple[int64, int64]]]: A list of possible moves for the player.
        """
        neighbors = []

        for dir in cardinal_directions:
            self.get_move_cardinal(node, dir, neighbors)

        if not self.cardinal_only:
            if self.walkable_diagonally:
                for dir in intermediate_directions:
                    self.get_move_intermediate(node, dir, neighbors)

        return neighbors

    def adjacents(self, node: Tuple[int64, int64]) -> List[Union[Any, Tuple[int64, int64]]]:
        adjacents = []

        for dir in cardinal_directions:
            adj = (node[0] + dir[0], node[1] + dir[1])
            if not (0 <= adj[0] < C.SIZE_Y and 0 <= adj[1] < C.SIZE_X):
                continue
            if self.bot.current_level.walkable[adj]:
                adjacents.append(adj)

        if not self.cardinal_only:
            for dir in intermediate_directions:
                adj = (node[0] + dir[0], node[1] + dir[1])
                if not (0 <= adj[0] < C.SIZE_Y and 0 <= adj[1] < C.SIZE_X):
                    continue
                if self.bot.current_level.walkable[adj]:
                    adjacents.append(adj)

        return adjacents

    def update(self):
        if self.bot.blstats.prop_mask & nethack.BL_MASK_LEV:
            self.levitating = True
        else:
            self.levitating = False

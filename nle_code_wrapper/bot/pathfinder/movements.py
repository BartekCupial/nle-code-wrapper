from typing import TYPE_CHECKING, Any, List, Tuple, Union

from nle_utils.glyph import C, G
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

    def __init__(self, bot: "Bot", allow_walking_through_traps: bool = True) -> None:
        self.bot: "Bot" = bot
        self.allow_walking_through_traps = allow_walking_through_traps

    @property
    def walkable_diagonally(self) -> bool:
        level = self.bot.current_level
        return level.dungeon_number != DungeonLevel.SOKOBAN

    def walkable_cardinal(self, pos: Tuple[int64, int64]) -> bool:
        level = self.bot.current_level
        walkable = level.walkable[pos] and not (level.objects[pos] in G.BOULDER)
        return walkable

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
        if self.walkable_cardinal(new_pos):
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

        if self.walkable_diagonally:
            for dir in intermediate_directions:
                self.get_move_intermediate(node, dir, neighbors)

        return neighbors

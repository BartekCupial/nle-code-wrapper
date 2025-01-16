from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Tuple, Union

import networkx as nx
import numpy as np
from nle.nethack import actions as A
from numpy import int64

from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.pathfinder.chebyshev_search import ChebyshevSearch
from nle_code_wrapper.bot.pathfinder.distance import chebyshev_distance
from nle_code_wrapper.bot.pathfinder.movements import Movements

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


def calc_direction(from_y: int64, from_x: int64, to_y: int64, to_x: int64) -> str:
    # sometimes you can be moved by a monster, or be stunned
    if not (abs(from_y - to_y) <= 1 and abs(from_x - to_x) <= 1):
        raise BotPanic(
            f"direction cannot be calculated: abs(from_y - to_y) {abs(from_y - to_y)}, abs(from_x - to_x) {abs(from_x - to_x)}"
        )

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
    """
    Pathfinder class to handle pathfinding and movement.
    """

    def __init__(self, bot: "Bot") -> None:
        self.bot: Bot = bot
        self.movements = bot.movements
        self.search = ChebyshevSearch(self.movements)

    @property
    def direction_movements(self) -> Dict[str, Tuple[int, int]]:
        return {
            "west": (0, -1),
            "east": (0, 1),
            "north": (-1, 0),
            "south": (1, 0),
            "northwest": (-1, -1),
            "northeast": (-1, 1),
            "southwest": (1, -1),
            "southeast": (1, 1),
        }

    def set_movements(self, movements: Movements):
        self.movements = movements

    def astar(
        self, start: Tuple[int64, int64], goal: Tuple[int64, int64]
    ) -> Union[Iterable[Tuple[int64, int64]], None]:
        return self.search.astar(start, goal)

    def distances(self, start: Tuple[int64, int64]) -> Dict[Tuple[int64, int64], float]:
        return self.search.distances(start)

    def get_path_to(self, goal: Tuple[int64, int64]) -> Union[List[Tuple[int64, int64]], None]:
        """
        Get path to goal using the A* algorithm.

        Args:
            goal (Tuple[int64, int64]): Goal position.
        Returns:
            Union[List[Tuple[int64, int64]], None]: Path to goal if exists, otherwise None.
        """

        result = self.get_path_from_to(self.bot.entity.position, goal)
        return result

    def get_path_from_to(
        self, start: Tuple[int64, int64], goal: Tuple[int64, int64]
    ) -> Union[List[Tuple[int64, int64]], None]:
        """
        Get path from start to goal using the A* algorithm.

        Args:
            start (Tuple[int64, int64]): Start position.
            goal (Tuple[int64, int64]): Goal position.

        Returns:
            List[Tuple[int64, int64]]: Path from start
        """
        result = self.search.astar(start, goal)
        if result is None:
            return None
        else:
            return list(result)

    def random_move(self) -> None:
        """
        Randomly move the bot in any direction.
        """
        movements = [
            A.CompassDirection.N,
            A.CompassDirection.S,
            A.CompassDirection.E,
            A.CompassDirection.W,
            A.CompassDirection.NE,
            A.CompassDirection.SE,
            A.CompassDirection.NW,
            A.CompassDirection.SW,
        ]
        action = movements[np.random.choice(len(movements))]
        self.bot.step(action)

    def direction(self, pos: Tuple[int64, int64]) -> None:
        """
        Move the bot in the direction of the given position.

        Args:
            pos (Tuple[int64, int64]): Position to move
        """
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

    def move(self, dir: Tuple[int64, int64]) -> None:
        """
        Move the bot once to a square in the neighbourhood. Raises BotPanic
        if the bot position does not match the given position.

        Args:
            dir (Tuple[int64, int64]): Position to move
        """
        self.direction(dir)

        if self.bot.entity.position != dir:
            raise BotPanic(
                f'agent position do not match after "move": '
                f"expected ({dir[0]}, {dir[1]}), got ({self.bot.entity.position[0]}, {self.bot.entity.position[1]})"
            )

    def goto(self, goal: Tuple[int64, int64], fast: bool = False) -> bool:
        """
        Move the bot to the given goal position. If the goal is not reachable, raise BotPanic.

        Args:
            goal (Tuple[int64, int64]): Goal position.
            fast (bool): Whether to use fast_goto or not.
        Returns:
            bool: True if the bot successfully reaches the goal, False otherwise.
        """
        cont = True
        while cont and self.bot.entity.position != goal:
            path = self.get_path_to(goal)
            if path is None:
                raise BotPanic("end point is no longer accessible")
            path = path[1:]

            # TODO: implement fast_goto
            # if fast and len(path) > 2:
            #     my_position = bot.entity.position
            #     bot.pathfinder.fast_go_to()

            for point in path:
                # TODO: check if there is peaceful monster
                cardinal = np.abs(np.array(self.bot.entity.position) - point).sum() == 1
                if cardinal:
                    walkable = self.movements.walkable_cardinal(point)
                else:
                    walkable = self.movements.walkable_intermediate(self.bot.entity.position, point)
                if not walkable:
                    cont = True
                    break
                self.move(point)
            else:
                cont = False

        return True

    def distance(self, n1: Tuple[int64, int64], n2: Tuple[int64, int64]) -> int64:
        return chebyshev_distance(n1, n2)

    def neighbors(self, pos: Tuple[int64, int64], cardinal_only: bool = False) -> List[Union[Any, Tuple[int64, int64]]]:
        return self.movements.neighbors(pos, cardinal_only=cardinal_only)

    def reachable_adjacent(
        self, start: Tuple[int64, int64], goal: Tuple[int64, int64]
    ) -> Union[Tuple[int64, int64], bool]:
        """
        Check if the goal is reachable from the start position.

        Args:
            start (Tuple[int64, int64]): Start position.
            goal (Tuple[int64, int64]): Goal position.
        Returns:
            Union[Tuple[int64, int64], bool]: Return the position of the reachable adjacent node or False if not reachable.
        """

        distances = self.distances(start)
        neighbors = self.neighbors(goal)

        n_dist = []
        for n in neighbors:
            if n in distances:
                n_dist.append(distances[n])
            else:
                n_dist.append(np.inf)

        if len(n_dist) == 0:
            return False

        if min(n_dist) == np.inf:
            return False

        idx = np.argmin(n_dist)
        return neighbors[idx]

    def create_movements_graph(
        self, position_matrix: np.ndarray, cardinal_only: bool = False, start_count: int = 0
    ) -> nx.Graph:
        """
        Creates a networkx graph from a boolean position matrix where nodes represent True positions
        and edges connect positions that are neighbors according to self.neighbors().

        Args:
            position_matrix (np.ndarray): Boolean matrix where True values represent valid positions
            start_count (int, optional): Starting index for node numbering. Defaults to 0.

        Returns:
            nx.Graph: Graph with nodes representing positions and edges connecting neighboring positions
        """
        graph = nx.Graph()

        # Get all valid positions (where position_matrix is True)
        positions = np.argwhere(position_matrix)

        # Map each valid position to a node index
        pos_to_node = {tuple(pos): idx + start_count for idx, pos in enumerate(positions)}

        # Add all valid positions as nodes
        graph.add_nodes_from(pos_to_node.values())

        # For each position, add edges to any valid neighbor
        for pos, node_id in pos_to_node.items():
            for nbr in self.neighbors(pos, cardinal_only=cardinal_only):
                if nbr in pos_to_node:
                    graph.add_edge(node_id, pos_to_node[nbr])

        # Store the (row, col) positions as an attribute on each node
        nx.set_node_attributes(graph, {node_id: pos for pos, node_id in pos_to_node.items()}, name="positions")

        return graph

    def update(self):
        self.movements.update()

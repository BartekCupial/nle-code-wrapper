from collections import deque
from itertools import pairwise
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union

import networkx as nx
import numpy as np
from nle.nethack import actions as A
from nle_utils.glyph import G
from numpy import int64

from nle_code_wrapper.bot.exceptions import BotPanic, UnexpectedPotion

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


direction_to_action = {
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
}


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
        self.trap_cost = 10
        self._graph_cache = {}

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

    def create_movements_graph(self, no_cache: bool = False):
        if no_cache:
            return self._create_movements_graph()

        key = (
            self.bot.movements.allow_walking_through_traps,
            self.bot.movements.levitating,
            self.bot.movements.cardinal_only,
            self.bot.movements.monster_collision,
        )

        # cache the graph for the start position
        if key not in self._graph_cache:
            self._graph_cache[key] = self._create_movements_graph()

        return self._graph_cache[key]

    def _create_movements_graph(self, start_count: int = 0) -> nx.Graph:
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
        pos_to_node = {}
        node_counter = start_count

        # Queue for BFS: (position, steps_taken)
        start_position = self.bot.entity.position
        queue = deque([start_position])
        seen = {start_position}

        pos_to_node[start_position] = node_counter
        graph.add_node(node_counter)
        node_counter += 1

        while queue:
            current_pos = queue.popleft()
            current_node = pos_to_node[current_pos]

            # Check all neighbors
            for nbr in self.neighbors(current_pos):
                nbr_node = pos_to_node.get(nbr)

                if nbr_node is not None:
                    # If neighbor already exists, just add edge if not present
                    if not graph.has_edge(current_node, nbr_node):
                        # Calculate edge weight based on trap presence
                        weight = 1  # Default weight
                        if self.bot.current_level.objects[nbr] in G.TRAPS:
                            weight += self.trap_cost
                        graph.add_edge(current_node, nbr_node, weight=weight)
                    continue

                if nbr in seen:
                    continue

                # Add new position to graph
                pos_to_node[nbr] = node_counter
                graph.add_node(node_counter)

                # Add weighted edge
                weight = 1
                if self.bot.current_level.objects[nbr] in G.TRAPS:
                    weight += self.trap_cost
                graph.add_edge(pos_to_node[current_pos], node_counter, weight=weight)

                # Add to BFS queue
                queue.append(nbr)
                seen.add(nbr)
                node_counter += 1

        # Store the (row, col) positions as node attributes
        nx.set_node_attributes(graph, {node_id: pos for pos, node_id in pos_to_node.items()}, name="positions")

        return graph

    def distances(self, start_pos: Tuple[int64, int64]) -> dict:
        """
        Returns a dictionary where the keys are graph node IDs and
        the values are their distance from the given start_node.
        """
        graph = self.create_movements_graph()
        start_node = [node for node in graph.nodes if graph._node[node]["positions"] == start_pos]
        if start_node:
            start_node = start_node[0]
        else:
            return {}

        # Use NetworkX's single_source_shortest_path_length to compute distances
        node_distances = dict(nx.single_source_shortest_path_length(graph, start_node))

        node_positions = nx.get_node_attributes(graph, "positions")
        position_distances = {node_positions[node]: distance for node, distance in node_distances.items()}

        return position_distances

    def distance(self, n1: Tuple[int64, int64], n2: Tuple[int64, int64]) -> int64:
        distances = self.distances(n1)
        return distances.get(n2, np.inf)

    def get_path_from_to(
        self,
        start: Tuple[int64, int64],
        goal: Tuple[int64, int64],
        no_cache: bool = False,
    ) -> Union[List[Tuple[int64, int64]], None]:
        graph = self.create_movements_graph(no_cache=no_cache)

        # Convert positions to node IDs
        node_positions = nx.get_node_attributes(graph, "positions")
        node_to_pos = {tuple(pos): node for node, pos in node_positions.items()}

        # Get node IDs for start and end positions
        start_node = node_to_pos[tuple(start)]
        # TODO:
        # if tuple(goal) in node_to_pos:
        # TypeError: 'NoneType' object is not iterable
        if tuple(goal) in node_to_pos:
            end_node = node_to_pos[tuple(goal)]
        else:
            return None  # End point not reachable

        try:
            # Find shortest path using NetworkX
            path_nodes = nx.shortest_path(graph, start_node, end_node)

            # Convert path nodes back to positions
            path_positions = [node_positions[node] for node in path_nodes]
            return path_positions

        except nx.NetworkXNoPath:
            return None  # No path exists between the points

    def get_path_to(self, goal: Tuple[int64, int64], no_cache: bool = False) -> Union[List[Tuple[int64, int64]], None]:
        """
        Get path to goal using the A* algorithm.

        Args:
            goal (Tuple[int64, int64]): Goal position.
        Returns:
            Union[List[Tuple[int64, int64]], None]: Path to goal if exists, otherwise None.
        """

        result = self.get_path_from_to(self.bot.entity.position, goal, no_cache=no_cache)
        return result

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
        self.bot.step(direction_to_action[dir])

    def move(self, dir: Tuple[int64, int64]) -> None:
        """
        Move the bot once to a square in the neighbourhood. Raises BotPanic
        if the bot position does not match the given position.

        Args:
            dir (Tuple[int64, int64]): Position to move
        """
        self.direction(dir)

        if self.bot.entity.position != dir:
            raise UnexpectedPotion(
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
        if fast:
            path = self.get_path_to(goal)
            if path is None:
                raise BotPanic("end point is no longer accessible")
            if len(path) > 2:
                self.fast_goto(goal)

        cont = True
        while cont and self.bot.entity.position != goal:
            path = self.get_path_to(goal)
            if path is None:
                raise BotPanic("end point is no longer accessible")
            path = path[1:]

            for point in path:
                # TODO: check if there is peaceful monster
                cardinal = np.abs(np.array(self.bot.entity.position) - point).sum() == 1
                if cardinal:
                    walkable = self.bot.movements.walkable_cardinal(self.bot.entity.position, point)
                else:
                    walkable = self.bot.movements.walkable_intermediate(self.bot.entity.position, point)
                if not walkable:
                    cont = True
                    break
                self.move(point)
            else:
                cont = False

        return True

    def move_cursor(self, goal):
        cursor_position = self.bot.entity.position

        # Create list of points between current position and goal
        points = []
        start_y, start_x = cursor_position
        end_y, end_x = goal

        # Calculate deltas
        dy = end_y - start_y
        dx = end_x - start_x
        steps = max(abs(dy), abs(dx))

        if steps == 0:
            return

        # Generate points with diagonal movement when possible
        for i in range(steps + 1):
            y = start_y + round(dy * (i / steps))
            x = start_x + round(dx * (i / steps))
            points.append((y, x))

        # Iterate over consecutive pairs of points
        for p1, p2 in pairwise(points):
            # Calculate direction between consecutive points
            dir = calc_direction(p1[0], p1[1], p2[0], p2[1])
            # Execute the movement
            self.bot.step(direction_to_action[dir])

    def fast_goto(self, goal):
        self.bot.step(A.Command.TRAVEL)
        self.move_cursor(goal)
        self.bot.step(A.MiscDirection.WAIT)

    def glance(self, goal):
        self.bot.step(A.Command.GLANCE)
        self.move_cursor(goal)
        self.bot.step(A.Command.GLANCE)

    def neighbors(self, pos: Tuple[int64, int64]) -> List[Union[Any, Tuple[int64, int64]]]:
        return self.bot.movements.neighbors(pos)

    def adjacents(self, pos: Tuple[int64, int64]) -> List[Union[Any, Tuple[int64, int64]]]:
        return self.bot.movements.adjacents(pos)

    def reachable(
        self, start: Tuple[int64, int64], goal: Tuple[int64, int64], adjacent: bool = False
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
        positions = self.adjacents(goal) if adjacent else self.neighbors(goal)

        n_dist = []
        for n in positions:
            if n in distances:
                n_dist.append(distances[n])
            else:
                n_dist.append(np.inf)

        if len(n_dist) == 0:
            return None

        if min(n_dist) == np.inf:
            return None

        idx = np.argmin(n_dist)
        return positions[idx]

    def update(self):
        self._graph_cache.clear()

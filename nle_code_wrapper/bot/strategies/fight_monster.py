from typing import List, Tuple

import networkx as nx
import numpy as np

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.pathfinder.distance import cross_distance
from nle_code_wrapper.bot.strategies.goto import goto_closest
from nle_code_wrapper.bot.strategy import repeat, strategy


@strategy
def fight_monster(bot: "Bot") -> bool:
    """
    Directs the bot to fight the closest monster.
    This function finds the closest monster entity that the bot can reach using its pathfinder.
    If a reachable monster is found, the bot will attack it and the function will return True.
    If no reachable monster is found, the function will return False.
    Args:
        bot (Bot): The bot instance that will perform the action.
    Returns:
        bool: True if the bot attacks a monster, False otherwise.
    """

    entity = min(
        (e for e in bot.entities if bot.pathfinder.get_path_to(e.position)),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
        default=None,
    )

    if entity:
        bot.pvp.attack_melee(entity)
        return True
    else:
        return False


@strategy
@repeat
def wait_for_monster(bot: "Bot") -> bool:
    nearby_monsters = [e for e in bot.entities if bot.pathfinder.get_path_to(e.position)]

    if not nearby_monsters:
        return False

    # check if monsters are in attack range
    for monster in nearby_monsters:
        if bot.pathfinder.distance(monster.position, bot.entity.position) == 1:
            return False

    # Wait for monsters to come to us
    bot.wait()

    return True


@strategy
@repeat
def fight_multiple_monsters(bot: "Bot") -> bool:
    nearby_monsters = [e for e in bot.entities if bot.pathfinder.get_path_to(e.position)]

    if not nearby_monsters:
        return False

    if len(nearby_monsters) == 1:
        bot.pvp.attack_melee(nearby_monsters[0])
        return True

    # Find tactical positions: corridor ends and doorways
    tactical_positions = find_tactical_positions(bot, nearby_monsters)

    # If we're already at a tactical position
    if bot.entity.position in tactical_positions:
        # Attack any monster in range
        for monster in nearby_monsters:
            if bot.pathfinder.distance(monster.position, bot.entity.position) == 1:
                bot.pvp.attack_melee(monster)
                return True
        # Wait for monsters to come to us
        bot.wait()
        return True

    if len(tactical_positions) > 0:
        # Move to nearest tactical position
        goto_closest(bot, tactical_positions)
        return True

    # If no tactical positions are found, attack the closest monster
    entity = min(
        (e for e in nearby_monsters),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
    )
    bot.pvp.attack_melee(entity)
    return True


@strategy
def goto_tactical_position(bot: "Bot") -> bool:
    nearby_monsters = [e for e in bot.entities if bot.pathfinder.get_path_to(e.position)]
    tactical_positions = find_tactical_positions(bot, nearby_monsters)

    if len(tactical_positions) > 0:
        # Move to nearest tactical position
        goto_closest(bot, tactical_positions)
        return True
    else:
        return False


def find_tactical_positions(bot: "Bot", nearby_monsters: List[Entity]) -> List[Tuple]:
    """
    Finds positions which allows the bot to fight multiple monsters one at a time.
    """
    tactical_spots = []

    # TODO: move graph to bot.pathfinder
    graph = nx.Graph()
    count = 0
    positions = np.argwhere(bot.current_level.walkable)
    nodes = range(count, count + len(positions))
    graph.add_nodes_from(nodes)
    graph.add_edges_from(np.argwhere(cross_distance(positions, positions) == 1).tolist())

    nx.set_node_attributes(graph, dict(zip(nodes, positions)), "positions")

    def count_reachable_monsters(spot, monsters):
        reachable_count = 0
        neighbors = bot.pathfinder.neighbors(spot)

        for neighbor in neighbors:
            for monster in monsters:
                # Check if there's a path from monster to neighbor, excluding the spot itself
                path = bot.pathfinder.get_path_from_to(monster.position, neighbor)
                if spot not in path:
                    reachable_count += 1
                    break  # Count this neighbor and move to the next

        return reachable_count

    def is_good_tactical_spot(spot, monsters):
        reachable_monsters = count_reachable_monsters(spot, monsters)
        return reachable_monsters <= 1

    # Find articulation points (potential corridor/chokepoint positions)
    for node in nx.articulation_points(graph):
        pos = tuple(graph._node[node]["positions"])
        # Check neighbors of articulation points
        for neighbor in bot.pathfinder.neighbors(pos):
            if is_good_tactical_spot(neighbor, nearby_monsters):
                tactical_spots.append(neighbor)

    # Remove duplicates while preserving order
    tactical_spots = list(dict.fromkeys(tactical_spots))

    return tactical_spots

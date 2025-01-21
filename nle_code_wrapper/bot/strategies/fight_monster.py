from typing import List, Tuple

import networkx as nx
import numpy as np
from nle.nethack import actions as A

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.strategies.goto import goto_closest
from nle_code_wrapper.bot.strategy import repeat, strategy


@strategy
def fight_monster(bot: "Bot") -> bool:
    """
    Directs the bot to fight melee the closest monster.
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
def fight_engulfed(bot: "Bot") -> bool:
    ret = False
    while bot.engulfed:
        # TODO: zap wand of digging if we have it
        # guaranteed attack
        bot.step(A.CompassCardinalDirection.W)
        ret = True

    return ret


@strategy
@repeat
def wait_for_monster(bot: "Bot") -> bool:
    """
    Makes the bot wait for monsters to come within attack range.
    """
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
    """
    Tactical combat behavior whenwhen fighting swarms of enemies.
    The bot will seek choke points, wait for the enemies and fight them one by one.
    """

    # Find tactical positions: corridor ends and doorways
    distances = bot.pathfinder.distances(bot.entity.position)
    nearby_monsters = [e for e in bot.entities if distances.get(e.position, None)]
    if not nearby_monsters:
        return False
    tactical_positions = find_tactical_positions(bot, nearby_monsters)

    # if only one monster fight it
    if len(nearby_monsters) == 1:
        bot.pvp.attack_melee(nearby_monsters[0])
        return True
    else:
        # if there is more monsters go to a tacical position if there are any
        if len(tactical_positions) > 0:
            # goto a tactical position if you are not in one
            if bot.entity.position not in tactical_positions:
                goto_closest(bot, tactical_positions)

            # when you are in tactical positions and there are multiple monsters wait for them to come to you
            while True:
                # Update distances and nearby monsters
                distances = bot.pathfinder.distances(bot.entity.position)
                adjacent_monsters = [e for e in bot.entities if distances.get(e.position, np.inf) == 1]

                if len(adjacent_monsters) == 0:
                    # Wait for monsters to approach
                    bot.wait()
                elif len(adjacent_monsters) == 1:
                    # Attack the adjacent monster
                    bot.pvp.attack_melee(adjacent_monsters[0])
                    return True
                else:
                    # we are surrounded, give control back to the high lecel policy
                    return False
        else:
            # If no tactical positions are found, attack the closest monster
            distances = bot.pathfinder.distances(bot.entity.position)
            entity = min(
                nearby_monsters,
                key=lambda e: distances[e.position],
            )
            bot.pvp.attack_melee(entity)
            return True


@strategy
def goto_choke_point(bot: "Bot") -> bool:
    """
    Directs the bot to move to the nearest choke point.
    """
    distances = bot.pathfinder.distances(bot.entity.position)
    nearby_monsters = [e for e in bot.entities if distances.get(e.position, None)]
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

    # TODO we can fight diagonally through doors even when we cannot move there
    # use separate movements
    graph = bot.pathfinder.create_movements_graph(bot.entity.position)

    def is_good_tactical_spot(tactical_spot, choke_pos, monsters):
        for monster in monsters:
            # Check if there's a path from monster to neighbor
            path = bot.pathfinder.get_path_from_to(tactical_spot, monster.position)
            if path is None:
                continue

            # if choke point is not in the path, tactical spot is on the wrong side of the choke
            # or we can be surrounded by monsters coming from both sides
            if choke_pos not in path:
                return False

        return True

    # Find articulation points (potential corridor/chokepoint positions)
    for choke in nx.articulation_points(graph):
        choke_pos = tuple(graph._node[choke]["positions"])
        # Check neighbors of articulation points
        for neighbor in bot.pathfinder.neighbors(choke_pos):
            if is_good_tactical_spot(neighbor, choke_pos, nearby_monsters):
                tactical_spots.append(neighbor)

    return tactical_spots

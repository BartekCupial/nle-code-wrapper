from typing import List, Tuple

import networkx as nx
import numpy as np
from nle.nethack import actions as A

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.character.properties import Alignment, Race
from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.pathfinder.movements import Movements
from nle_code_wrapper.bot.pvp.monster import MonsterClassTypes
from nle_code_wrapper.bot.strategies.goto import goto_closest
from nle_code_wrapper.bot.strategy import repeat, strategy


@strategy
def fight_melee(bot: "Bot") -> bool:
    """
    Directs the bot to fight melee the closest monster.
    Prioritizes hostile monsters.
    """
    bot.movements = Movements(bot, monster_collision=False)

    def is_peaceful(bot: "Bot", entity: Entity):
        check = False

        # always peaceful
        if entity.name in MonsterClassTypes.always_peaceful(entity.name):
            check = True

        # sometimes peaceful lawful
        if bot.character.alignment == Alignment.LAWFUL:
            if entity.name in MonsterClassTypes.sometimes_peaceful_lawful(entity.name):
                check = True

        # sometimes peaceful neutral
        if bot.character.alignment == Alignment.NEUTRAL:
            if entity.name in MonsterClassTypes.sometimes_peaceful_neutral(entity.name):
                check = True

        # sometimes peaceful chaotic
        if bot.character.alignment == Alignment.CHAOTIC:
            if entity.name in MonsterClassTypes.sometimes_peaceful_chaotic(entity.name):
                check = True

        # check humans, elves, dwarves, humans and gnomes
        if bot.character.race == Race.HUMAN:
            pass
        elif bot.character.race == Race.ELF:
            if ord(entity.permonst.mlet) in [MonsterClassTypes.S_ELF]:
                check = True
        elif bot.character.race == Race.DWARF:
            if ord(entity.permonst.mlet) in [MonsterClassTypes.S_DWARF, MonsterClassTypes.S_GNOME]:
                check = True
        elif bot.character.race == Race.GNOME:
            if ord(entity.permonst.mlet) in [MonsterClassTypes.S_DWARF, MonsterClassTypes.S_GNOME]:
                check = True
        elif bot.character.race == Race.ORC:
            pass

        if check:
            bot.pathfinder.glance(entity.position)
            return "peaceful" in bot.message
        else:
            return False

    # def is_peaceful(bot: "Bot", entity: Entity):
    #     return False

    neighbors = [bot.pathfinder.reachable(bot.entity.position, e.position, adjacent=True) for e in bot.entities]
    distances = bot.pathfinder.distances(bot.entity.position)

    # Create list of tuples (neighbor, entity, is_peaceful)
    entities_info = [
        (neighbor, entity, is_peaceful(bot, entity))
        for neighbor, entity in zip(neighbors, bot.entities)
        if neighbor is not None
    ]

    # First try to find the closest hostile monster
    hostile_targets = [(neighbor, entity) for neighbor, entity, peaceful in entities_info if not peaceful]

    if hostile_targets:
        # Attack closest hostile monster
        adjacent, entity = min(hostile_targets, key=lambda pair: distances.get(pair[0], np.inf))
        bot.pvp.attack_melee(entity)
        return True

    # If no hostile monsters, try peaceful ones
    peaceful_targets = [(neighbor, entity) for neighbor, entity, peaceful in entities_info if peaceful]

    if peaceful_targets:
        # Attack closest peaceful monster
        adjacent, entity = min(peaceful_targets, key=lambda pair: distances.get(pair[0], np.inf))
        bot.pvp.attack_melee(entity)
        return True

    return False


@strategy
def fight_ranged(bot: "Bot") -> bool:
    """
    Directs the bot to fight ranged the closest monster.
    """
    bot.movements = Movements(bot, monster_collision=False)

    neigbors = [bot.pathfinder.reachable(bot.entity.position, e.position, adjacent=True) for e in bot.entities]
    distances = bot.pathfinder.distances(bot.entity.position)
    adjacent, entity = min(
        ((neighbor, e) for neighbor, e in zip(neigbors, bot.entities) if neighbor is not None),
        key=lambda pair: distances.get(pair[0], np.inf),
        default=(None, None),
    )

    if entity:
        bot.pvp.attack_ranged(entity)
        return True
    else:
        return False


@strategy
def fight_engulfed(bot: "Bot") -> bool:
    """
    Fight while being inside the monster until you're out.
    """
    bot.movements = Movements(bot, monster_collision=False)

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
    Makes the bot wait for monsters to come within an attack range.
    """
    bot.movements = Movements(bot, monster_collision=False)

    nearby_monsters = [
        e for e in bot.entities if bot.pathfinder.reachable(bot.entity.position, e.position, adjacent=True) is not None
    ]
    if not nearby_monsters:
        return False

    # check if monsters are in attack range
    for monster in nearby_monsters:
        if bot.entity.position in bot.pathfinder.adjacents(monster.position):
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
    bot.movements = Movements(bot, monster_collision=False)

    # Find tactical positions: corridor ends and doorways
    nearby_monsters = [
        e for e in bot.entities if bot.pathfinder.reachable(bot.entity.position, e.position, adjacent=True) is not None
    ]
    if not nearby_monsters:
        return False
    tactical_positions = find_tactical_positions(bot, bot.entities)

    # if there is more monsters go to a tacical position if there are any
    if len(tactical_positions) > 0:
        # goto a tactical position if you are not in one
        if bot.entity.position not in tactical_positions:
            goto_closest(bot, tactical_positions)

        # when you are in tactical positions and there are multiple monsters wait for them to come to you
        while True:
            # Update distances and nearby monsters
            adjacent_monsters = [e for e in bot.entities if bot.entity.position in bot.pathfinder.adjacents(e.position)]

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
        return fight_melee(bot)


@strategy
def goto_choke_point(bot: "Bot") -> bool:
    """
    Directs the bot to move to the nearest choke point.
    """
    bot.movements = Movements(bot, monster_collision=False)

    tactical_positions = find_tactical_positions(bot, bot.entities)

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

    def is_good_tactical_spot(tactical_spot):
        # count number of monster that can hit
        number_of_tiles_reachable = 0
        for adjacent in bot.pathfinder.adjacents(tactical_spot):
            for monster in nearby_monsters:
                reachable = bot.pathfinder.reachable(adjacent, monster.position)
                if reachable is None:
                    continue

                path = bot.pathfinder.get_path_from_to(adjacent, reachable)
                if path is None:
                    continue

                if tactical_spot not in path:
                    number_of_tiles_reachable += 1
                    break

        return number_of_tiles_reachable == 1

    graph = bot.pathfinder.create_movements_graph(bot.entity.position)

    tactical_spots = []
    # Find articulation points (potential corridor/chokepoint positions)
    for choke in nx.articulation_points(graph):
        choke_pos = tuple(graph._node[choke]["positions"])
        # Check neighbors of articulation points
        for neighbor in bot.pathfinder.adjacents(choke_pos):
            if is_good_tactical_spot(neighbor):
                tactical_spots.append(neighbor)

    return tactical_spots

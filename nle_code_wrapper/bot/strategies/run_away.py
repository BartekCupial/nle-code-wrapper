from typing import List, Optional, Tuple

from numpy import int64

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.strategy import repeat, strategy


@strategy
@repeat
def run_away(bot: "Bot") -> bool:
    """
    Moves away the bot in the opposite direction of nearby monsters,
    """

    # Get all nearby monsters
    nearby_monsters = [e for e in bot.entities if bot.pathfinder.get_path_to(e.position)]

    if len(nearby_monsters) > 0:
        # Too many enemies nearby, move one square away
        escape_position = find_escape_position(bot, nearby_monsters)
        if escape_position:
            bot.pathfinder.goto(escape_position)
            return True
        else:
            return False
    else:
        return False


def find_escape_position(bot: "Bot", monsters: List[Entity]) -> Optional[Tuple[int64, int64]]:
    """
    Finds the best escape position for the bot given a list of monsters.

    Args:
        bot (Bot): The bot instance executing the strategy.
        monsters (List[Entity]): The list of monsters to escape from.

    Returns:
        Optional[Tuple[int64, int64]]: The escape position if found, None otherwise.
    """
    current_pos = bot.entity.position
    neighbors = bot.pathfinder.neighbors(current_pos)

    def neighbor_to_monsters_distance(n):
        return sum([bot.pathfinder.distance(n, m.position) for m in monsters])

    current_distance = neighbor_to_monsters_distance(bot.entity.position)

    escape_position = max(
        (e for e in neighbors if neighbor_to_monsters_distance(e) > current_distance),
        key=lambda e: neighbor_to_monsters_distance(e),
        default=None,
    )

    return escape_position

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def fight_closest_monster(bot: "Bot") -> bool:
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
        path = bot.pathfinder.get_path_to(entity.position)
        orig_path = list(path)
        path = orig_path[1:]

        for point in path:
            if bot.pathfinder.distance(bot.entity.position, entity.position) > 1:
                bot.pathfinder.move(point)
            else:
                bot.pathfinder.direction(entity.position)

            # if the enemy is not at original position stop attacking
            # either enemy is dead or it moved
            if len([e for e in bot.entities if e.position == entity.position and e.name == entity.name]) == 0:
                break

        return True
    else:
        return False


def fight_all_monsters(bot: "Bot") -> None:
    # kill all reachable monsters
    while True:
        fighting = fight_closest_monster(bot)
        if not fighting:
            break

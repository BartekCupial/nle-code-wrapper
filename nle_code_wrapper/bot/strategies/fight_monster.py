from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


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

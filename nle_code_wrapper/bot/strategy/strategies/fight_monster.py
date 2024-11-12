from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategy import Strategy


@Strategy.wrap
def fight_closest_monster(bot: "Bot"):
    """
    Directs the bot to fight the closest monster.
    This function finds the closest monster entity that the bot can reach using its pathfinder.
    If a reachable monster is found, the bot will attack it and the function will yield True.
    If no reachable monster is found, the function will yield False.
    Args:
        bot (Bot): The bot instance that will perform the action.
    Yields:
        bool: True if the bot attacks a monster, False otherwise.
    """

    entity = min(
        (e for e in bot.entities if bot.pathfinder.get_path_to(e.position)),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
        default=None,
    )

    if entity:
        bot.pvp.attack(entity)
        yield True
    else:
        yield False


@Strategy.wrap
def fight_all_monsters(bot: "Bot"):
    fight_strategy = fight_closest_monster(bot)

    # kill all reachable monsters
    while True:
        fighting = fight_strategy()
        if not fighting:
            break

    yield

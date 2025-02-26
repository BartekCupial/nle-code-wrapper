from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.pathfinder.movements import Movements
from nle_code_wrapper.bot.strategy import strategy


@strategy
def approach_monster(bot: "Bot"):
    """
    Moves bot in the direction of closest monster until it gets whithin range of wands.
    """

    bot.movements = Movements(bot, monster_collision=False)

    entity = min(
        (e for e in bot.entities if bot.pathfinder.get_path_to(e.position)),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
        default=None,
    )

    if entity:
        bot.pvp.approach(entity, distance=7)
        return True
    else:
        return False


@strategy
def zap_monster(bot: "Bot") -> bool:
    """
    Zaps closest monster with a wand.
    Tip:
    - you need a wand
    - takes into account wall reflections so you won't zap yourself
    """

    bot.movements = Movements(bot, monster_collision=False)

    entity = min(
        (e for e in bot.entities if bot.pathfinder.get_path_to(e.position)),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
        default=None,
    )

    if entity:
        return bot.pvp.zap(entity)
    else:
        return False


@strategy
def approach_and_zap_monster(bot: "Bot"):
    """
    Combines 'approach_monster' and 'zap_monster'.
    """

    bot.movements = Movements(bot, monster_collision=False)

    entity = min(
        (e for e in bot.entities if bot.pathfinder.get_path_to(e.position)),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
        default=None,
    )

    if entity:
        return bot.pvp.approach_and_zap(entity)
    else:
        return False

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def approach_monster(bot: "Bot"):
    entity = min(
        (e for e in bot.entities if bot.pathfinder.get_path_to(e.position)),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
        default=None,
    )

    if entity:
        bot.pvp.approach(entity, distance=3)
        return True
    else:
        return False


@strategy
def zap_monster(bot: "Bot") -> bool:
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
    entity = min(
        (e for e in bot.entities if bot.pathfinder.get_path_to(e.position)),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
        default=None,
    )

    if entity:
        return bot.pvp.approach_and_zap(entity)
    else:
        return False

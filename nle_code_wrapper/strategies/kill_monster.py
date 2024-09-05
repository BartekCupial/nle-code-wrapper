from nle_code_wrapper.bot.bot import Bot


def kill_monster(bot: "Bot", monster_name: str):
    entity = min(
        (e for e in bot.entities if e.name == monster_name and bot.pathfinder.get_path_to(bot.entity.position)),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
        default=None,
    )

    if entity:
        bot.pvp.attack(entity)

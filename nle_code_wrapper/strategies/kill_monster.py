from nle_code_wrapper.bot.bot import Bot


def kill_monster(bot: "Bot", monster_name: str):
    entity = min(
        (e for e in bot.entities if e.name == monster_name and bot.pathfinder.get_path_to(e.position)),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
        default=None,
    )

    if entity:
        bot.pvp.attack(entity)


def kill_all_monsters(bot: "Bot"):
    # kill all reachable monsters
    while len([e for e in bot.entities if bot.pathfinder.get_path_to(e.position)]) > 0:
        monster_name = bot.entities[0].name
        kill_monster(bot, monster_name)

    yield

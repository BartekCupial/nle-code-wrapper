from nle_code_wrapper.bot.bot import Bot


def fight_closest_monster(bot: "Bot"):
    entity = min(
        (e for e in bot.entities if bot.pathfinder.get_path_to(e.position)),
        key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position),
        default=None,
    )

    if entity:
        bot.pvp.attack(entity)
        return True
    else:
        return False


def fight_all_monsters(bot: "Bot"):
    # kill all reachable monsters
    while fight_closest_monster(bot):
        pass

    yield

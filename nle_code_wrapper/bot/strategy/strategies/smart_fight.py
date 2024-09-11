from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategy import Strategy


@Strategy.wrap
def smart_fight_strategy(bot: "Bot"):
    # TODO: smart fight strategy isn't perfect
    # in the `fight_corridor` case it should stay in the corridor and wait for the enemies
    # instead it fights and when there are multiple enemies it backs up to the corridor
    # this means that sometimes it gets hit by multiple enemies at once before backing up

    # Get all nearby monsters
    nearby_monsters = [e for e in bot.entities if bot.pathfinder.get_path_to(e.position)]

    # Sort monsters by distance
    nearby_monsters.sort(key=lambda e: bot.pathfinder.distance(e.position, bot.entity.position))

    # Count enemies within attack range
    enemies_in_range = sum(1 for m in nearby_monsters if bot.pathfinder.distance(m.position, bot.entity.position) == 1)

    # multiple enemies
    if enemies_in_range > 1:
        # Too many enemies nearby, move one square away
        escape_position = find_escape_position(bot, nearby_monsters)
        if escape_position:
            bot.pathfinder.goto(escape_position)
            yield True
        else:
            yield False
    elif nearby_monsters:
        # Attack the closest monster
        closest_monster = nearby_monsters[0]
        bot.pvp.attack(closest_monster)
        yield True
    else:
        yield False


def find_escape_position(bot: "Bot", monsters):
    current_pos = bot.entity.position
    neighbors = bot.pathfinder.neighbors(current_pos)

    def neighbor_to_monsters_distance(n):
        return sum([bot.pathfinder.distance(n, m.position) for m in monsters])

    escape_position = max(
        (e for e in neighbors if neighbor_to_monsters_distance(e) >= 1),
        key=lambda e: neighbor_to_monsters_distance(e),
        default=None,
    )

    return escape_position

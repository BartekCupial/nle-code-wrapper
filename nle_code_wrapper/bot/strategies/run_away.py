from nle_code_wrapper.bot.bot import Bot


def run_away(bot: "Bot"):
    """
    Executes the run away strategy for the bot.
    This strategy involves the bot identifying nearby monsters,
    moving away to a safer position if possible.
    Args:
        bot (Bot): The bot instance executing the strategy.
    Yields:
        bool: True if the bot moves to an escape position, False otherwise.
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


def find_escape_position(bot: "Bot", monsters):
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

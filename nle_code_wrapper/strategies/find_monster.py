import numpy as np

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.strategies.kill_monster import kill_monster


def find_monster(bot: "Bot"):
    level = bot.current_level()

    # Create a matrix to store exploration priorities
    exploration_priority = np.zeros(level.seen.shape)

    # Find the highest priority location that is reachable
    while True:
        # kill all reachable monsters
        while len([e for e in bot.entities if bot.pathfinder.get_path_to(e.position)]) > 0:
            monster_name = bot.entities[0].name
            kill_monster(bot, monster_name)

        # if there is no monsters goto stairs
        if len(level.stairs) > 0:
            bot.pathfinder.goto(level.stairs[0])

        # Mark unexplored areas with high priority
        exploration_priority[level.walkable] = 1

        # Unmark explored areas with no priority
        exploration_priority[level.was_on] = 0

        goal = np.unravel_index(np.argmax(exploration_priority), exploration_priority.shape)
        bot.pathfinder.goto(goal)

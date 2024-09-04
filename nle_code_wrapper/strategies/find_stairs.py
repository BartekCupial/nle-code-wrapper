import numpy as np

from nle_code_wrapper.strategies.goto_stairs import goto_stairs


def find_stairs(bot):
    level = bot.current_level()

    # Create a matrix to store exploration priorities
    exploration_priority = np.zeros(level.seen.shape)

    # Find the highest priority location that is reachable
    while True:
        if len(level.stairs) > 0:
            goto_stairs(bot)

        # Mark unexplored areas with high priority
        exploration_priority[level.walkable] = 1

        # Unmark explored areas with no priority
        exploration_priority[level.was_on] = 0

        goal = np.unravel_index(np.argmax(exploration_priority), exploration_priority.shape)
        bot.pathfinder.goto(goal)

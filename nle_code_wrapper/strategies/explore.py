import numpy as np

from nle_code_wrapper.bot import Bot


def explore(bot: "Bot", condition):
    level = bot.current_level()

    # Create a matrix to store exploration priorities
    exploration_priority = np.zeros(level.seen.shape)

    # Find the highest priority location that is reachable
    while True:
        condition()

        distances = bot.pathfinder.distances(bot.entity.position)
        distance_indices = tuple(np.array(list(distances.keys())).T)
        distance_values = np.array(list(distances.values()))
        exploration_priority[distance_indices] = np.max(distance_values) - distance_values + 1

        # Unmark explored areas with no priority
        exploration_priority[level.was_on] = 0

        goal = np.unravel_index(np.argmax(exploration_priority), exploration_priority.shape)
        bot.pathfinder.goto(goal)

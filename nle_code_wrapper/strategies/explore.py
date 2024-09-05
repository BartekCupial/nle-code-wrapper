import numpy as np

from nle_code_wrapper.bot import Bot


def print_boolean_array_ascii(arr):
    for row in arr:
        print("".join([str(int(cell)) for cell in row]))


def explore(bot: "Bot"):
    # Find the highest priority location that is reachable
    level = bot.current_level()

    # Create a matrix to store exploration priorities
    exploration_priority = np.zeros(level.seen.shape)

    distances = bot.pathfinder.distances(bot.entity.position)
    distance_indices = tuple(np.array(list(distances.keys())).T)
    distance_values = np.array(list(distances.values()))
    exploration_priority[distance_indices] = distance_values
    exploration_priority[level.was_on] = 0
    unexplored = exploration_priority > 0
    exploration_priority[unexplored] = np.max(exploration_priority) - exploration_priority[unexplored] + 1

    goal = np.unravel_index(np.argmax(exploration_priority), exploration_priority.shape)
    bot.pathfinder.goto(goal)

    yield

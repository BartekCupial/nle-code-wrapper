import random

from nle.nethack import actions as A

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.exceptions import UnexpectedPotion
from nle_code_wrapper.bot.strategy import strategy


@strategy
def escape_trap(bot: "Bot"):
    """
    Makes multiple attempts to escape trap (up to 10 tries)
    """
    if bot.trap:
        for i in range(10):
            neighbors = bot.pathfinder.neighbors(bot.entity.position)

            # Separate diagonal and cardinal neighbors
            diagonal_neighbors = [
                n for n in neighbors if (n[0] - bot.entity.position[0]) != 0 and (n[1] - bot.entity.position[1]) != 0
            ]

            # Prioritize diagonal neighbors
            if diagonal_neighbors:
                neighbor = random.choice(diagonal_neighbors)
            else:
                # Fall back to any available neighbor
                neighbor = random.choice(neighbors)

            neighbor = random.choice(neighbors)
            try:
                bot.pathfinder.move(neighbor)
            except UnexpectedPotion:
                pass

            if not bot.trap:
                return True

    return False

import re

import numpy as np
from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import Item, ItemCategory
from nle_code_wrapper.bot.strategies.goto import goto_glyph, goto_room
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils.strategies import label_dungeon_features


@strategy
def leave_shop(bot: "Bot") -> bool:
    """
    Leaves the shop by moving to the shop door and exiting through it. Drops all unpaid items.
    """
    shopkeeper_positions = [entity.position for entity in bot.entities if entity.name == "shopkeeper"]
    if not shopkeeper_positions:
        return False

    # Drop all unpaid items
    bot.step(A.Command.DROPTYPE)

    # check if "u" exists
    if "Unpaid items" in bot.message:
        bot.type_text("u")

    bot.step(A.MiscAction.MORE)
    bot.step(A.Command.PICKUP)
    bot.step(A.TextCharacters.SPACE)

    # Features and shop id outside while so we keep them consistent
    labeled_features, num_rooms, num_corridors = label_dungeon_features(bot)
    shop_id = labeled_features[bot.entity.position]

    i = 0

    # while we are in the shop
    while labeled_features[bot.entity.position] == shop_id:
        # we can exit the shop
        if goto_room(bot):
            pass

        # the exit is blocked by shopkeeper
        else:
            shop_keepers = [entity.position for entity in bot.entities if entity.name == "shopkeeper"]

            distances = bot.pathfinder.distances(bot.entity.position)
            closest_shop_keeper = min(
                [sk for sk in shop_keepers if bot.pathfinder.reachable(bot.entity.position, sk)],
                key=lambda sk: distances.get(bot.pathfinder.reachable(bot.entity.position, sk), np.inf),
                default=None,
            )

            reach = bot.pathfinder.reachable(bot.entity.position, closest_shop_keeper)

            # if we are next to the shopkeeper wait until it moves
            if distances[reach] == 0:
                bot.wait()

            # goto the shopkeeper
            else:
                path = bot.pathfinder.get_path_to(reach)
                bot.pathfinder.move(path[1])

        i += 1

        if i > 50:
            bot.add_message("Couldn't leave the shop, something is blocking the exit.")
            break

    return True


@strategy
def buy_items_shop(bot: "Bot") -> bool:
    pass


@strategy
def sell_items_shop(bot: "Bot") -> bool:
    pass

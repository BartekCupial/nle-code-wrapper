import numpy as np
from nle.nethack import actions as A
from nle_utils.glyph import SS, G
from nle_utils.item import ItemClasses

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import GLYPH_TO_OBJECT
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils


@strategy
def open_container_kick(bot: "Bot"):
    """
    Attempts to open a container by kicking it to break the lock.
    """
    container_glyphs = frozenset(
        glyph
        for glyph, obj in GLYPH_TO_OBJECT.items()
        if obj["obj_class"] == chr(ItemClasses.TOOL.value)
        and obj["obj_name"]
        in [
            "large box",
            "chest",
            "ice box",
            "bag of tricks",
            "oilskin sack",
            "bag of holding",
            "sack",
            "bag of tricks",
        ]
    )
    containers = np.argwhere(utils.isin(bot.glyphs, container_glyphs))

    reachable_container = min(
        (tuple(container) for container in containers if bot.pathfinder.get_path_to(tuple(container))),
        key=lambda container: bot.pathfinder.distance(bot.entity.position, container),
        default=None,
    )

    if reachable_container:
        adjacent = bot.pathfinder.reachable(bot.entity.position, reachable_container, adjacent=True)
        bot.pathfinder.goto(adjacent)
        for _ in range(5):
            bot.step(A.Command.KICK)
            bot.pathfinder.direction(reachable_container)
            if "break open the lock!" in bot.message:
                break

    return "break open the lock!" in bot.message


@strategy
def open_container_key(bot: "Bot"):
    """
    Attempts to open a container using a key from the bot's inventory.
    """
    container_glyphs = frozenset(
        glyph
        for glyph, obj in GLYPH_TO_OBJECT.items()
        if obj["obj_class"] == chr(ItemClasses.TOOL.value)
        and obj["obj_name"]
        in [
            "large box",
            "chest",
            "ice box",
            "bag of tricks",
            "oilskin sack",
            "bag of holding",
            "sack",
            "bag of tricks",
        ]
    )
    containers = np.argwhere(utils.isin(bot.glyphs, container_glyphs))

    reachable_container = min(
        (tuple(container) for container in containers if bot.pathfinder.get_path_to(tuple(container))),
        key=lambda container: bot.pathfinder.distance(bot.entity.position, container),
        default=None,
    )

    if reachable_container:
        bot.pathfinder.goto(reachable_container)
        bot.step(A.Command.APPLY)
        if "What do you want to use or apply?" in bot.message:
            for tool in bot.inventory["tools"]:
                if tool.is_key:
                    bot.step(tool.letter)
                    break

            bot.step(A.MiscDirection.WAIT)
            bot.type_text("y")  # confirm unlocking

    return "You succeed in picking the lock." in bot.message


@strategy
def loot_container(bot: "Bot"):
    """
    Attempts to loot all items from an opened container.
    """
    container_glyphs = frozenset(
        glyph
        for glyph, obj in GLYPH_TO_OBJECT.items()
        if obj["obj_class"] == chr(ItemClasses.TOOL.value)
        and obj["obj_name"]
        in [
            "large box",
            "chest",
            "ice box",
            "bag of tricks",
            "oilskin sack",
            "bag of holding",
            "sack",
            "bag of tricks",
        ]
    )
    containers = np.argwhere(utils.isin(bot.glyphs, container_glyphs))

    reachable_container = min(
        (tuple(container) for container in containers if bot.pathfinder.get_path_to(tuple(container))),
        key=lambda container: bot.pathfinder.distance(bot.entity.position, container),
        default=None,
    )

    if reachable_container:
        bot.pathfinder.goto(reachable_container)

    bot.step(A.Command.LOOT)
    if "loot it?" in bot.message:
        bot.type_text("y")

        # check if we are in the popup window
        if bot.xwaitingforspace:
            bot.type_text("o")  # o - take something out
            # container can be empty
            if bot.xwaitingforspace:
                lines = bot.message.split("\n")
                if "Take out what?" in lines[0]:
                    bot.step(A.Command.PICKUP)
                else:
                    bot.type_text("A")  # A - Auto-select every item
                bot.step(A.MiscAction.MORE)  # confirm
                return True

    return False

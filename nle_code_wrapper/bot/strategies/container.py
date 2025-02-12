import numpy as np
from nle.nethack import actions as A
from nle_utils.glyph import SS, G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import NAME_TO_GLYPHS
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils

CONTAINER_NAMES = frozenset(
    [
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


class ContainerHelper:
    @staticmethod
    def get_container_glyphs():
        return frozenset(glyph for name in CONTAINER_NAMES for glyph in NAME_TO_GLYPHS[name])

    @staticmethod
    def find_nearest_container(bot: Bot):
        """Find the nearest reachable container."""
        container_glyphs = ContainerHelper.get_container_glyphs()
        containers = np.argwhere(utils.isin(bot.glyphs, container_glyphs))

        return min(
            (tuple(container) for container in containers if bot.pathfinder.get_path_to(tuple(container))),
            key=lambda container: bot.pathfinder.distance(bot.entity.position, container),
            default=None,
        )

    @staticmethod
    def is_container_below(bot: Bot):
        """Check if there's a container at current position."""
        bot.step(A.Command.LOOK)
        return any(name in bot.message for name in CONTAINER_NAMES)

    @staticmethod
    def navigate_to_container(bot: Bot, container_pos, adjacent=False):
        """Navigate to container or adjacent position."""
        if adjacent:
            adjacent_pos = next((neighbor for neighbor in bot.pathfinder.neighbors(container_pos)), None)
            if adjacent_pos:
                bot.pathfinder.goto(adjacent_pos)
                return True
        else:
            bot.pathfinder.goto(container_pos)
            return True
        return False


@strategy
def open_container_kick(bot: Bot):
    """Attempts to open a container by kicking it to break the lock."""

    def kick_container(bot: Bot, container_position):
        for _ in range(5):
            bot.step(A.Command.KICK)
            bot.pathfinder.direction(container_position)
            if "break open the lock!" in bot.message:
                return True
        return False

    if ContainerHelper.is_container_below(bot):
        container_position = bot.entity.position
        if ContainerHelper.navigate_to_container(bot, container_position, adjacent=True):
            return kick_container(bot, container_position)
    else:
        container_pos = ContainerHelper.find_nearest_container(bot)
        if container_pos and ContainerHelper.navigate_to_container(bot, container_pos, adjacent=True):
            return kick_container(bot, container_pos)

    return "break open the lock!" in bot.message


@strategy
def open_container_key(bot: Bot):
    """Attempts to open a container using a key from the bot's inventory."""

    def apply_key(bot: Bot):
        bot.step(A.Command.APPLY)
        if "What do you want to use or apply?" in bot.message:
            for tool in bot.inventory["tools"]:
                if tool.is_key:
                    bot.step(tool.letter)
                    break
            bot.step(A.MiscDirection.WAIT)
            bot.type_text("y")

    def is_unlock_successful(bot: Bot):
        success_messages = [
            "unlocking the chest",
            "unlocking the box",
            "picking the lock",
        ]
        return any(f"You succeed in {msg}." in bot.message for msg in success_messages)

    if ContainerHelper.is_container_below(bot):
        apply_key(bot)
    else:
        container_pos = ContainerHelper.find_nearest_container(bot)
        if container_pos and ContainerHelper.navigate_to_container(bot, container_pos):
            apply_key(bot)

    return is_unlock_successful(bot)


@strategy
def loot_container(bot: Bot):
    """Attempts to loot all items from an opened container."""

    def perform_looting(bot: Bot):
        bot.step(A.Command.LOOT)
        if "loot it?" not in bot.message:
            return False

        bot.type_text("y")
        if not bot.xwaitingforspace:
            return False

        bot.type_text("o")
        if bot.xwaitingforspace:
            lines = bot.message.split("\n")
            if "Take out what?" in lines[0]:
                bot.step(A.Command.PICKUP)
            else:
                bot.type_text("A")
            bot.step(A.MiscAction.MORE)
            return True
        return False

    if ContainerHelper.is_container_below(bot):
        return perform_looting(bot)

    container_pos = ContainerHelper.find_nearest_container(bot)
    if container_pos and ContainerHelper.navigate_to_container(bot, container_pos):
        return perform_looting(bot)

    return False

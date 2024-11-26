from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.utils import utils


def position_of_closest_object(bot, obj):
    coords = utils.coords(bot.glyphs, obj)
    distances = bot.pathfinder.distances(bot.entity.position)

    position = min(
        (e for e in coords if e in distances),
        key=lambda e: distances[e],
        default=None,
    )

    return position


def pickup_key(bot: "Bot"):
    position = position_of_closest_object(bot, G.TOOL_CLASS)

    if position:
        bot.pathfinder.goto(position)
        bot.step(A.Command.PICKUP)
        return True
    else:
        return False

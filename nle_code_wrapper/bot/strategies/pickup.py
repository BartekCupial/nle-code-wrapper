import numpy as np
from nle.nethack import actions as A
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.goto import goto_closest_glyph
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import corridor_detection, room_detection, save_boolean_array_pillow
from nle_code_wrapper.utils.utils import coords


@strategy
def pickup_closest_item(bot: "Bot", item=G.ITEMS):
    if goto_closest_glyph(bot, item):
        bot.step(A.Command.PICKUP)
        return True
    else:
        return False


def pickup_closest_wand(bot: "Bot"):
    pickup_closest_item(bot, G.WAND_CLASS)


def pickup_closest_ring(bot: "Bot"):
    pickup_closest_item(bot, G.RING_CLASS)


def pickup_closest_boots(bot: "Bot"):
    # TODO: we should distinguish boots and armor
    # it should be possile by using correct glyph
    pickup_closest_item(bot, G.ARMOR_CLASS)


def pickup_closest_horn(bot: "Bot"):
    # TODO: we should distinguish horn and tools
    # it should be possile by using correct glyph
    pickup_closest_item(bot, G.TOOL_CLASS)

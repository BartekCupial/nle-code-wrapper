from nle.nethack import actions as A
from nle_utils.glyph import G
from nle_utils.item import ItemClasses

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import GLYPH_TO_OBJECT
from nle_code_wrapper.bot.strategies.goto import goto_closest_glyph
from nle_code_wrapper.bot.strategy import strategy


@strategy
def pickup_closest_item(bot: "Bot", item=G.ITEMS):
    if goto_closest_glyph(bot, item):
        bot.step(A.Command.PICKUP)
        return True
    else:
        return False


def pickup_closest_wand(bot: "Bot"):
    return pickup_closest_item(bot, G.WAND_CLASS)


def pickup_closest_ring(bot: "Bot"):
    return pickup_closest_item(bot, G.RING_CLASS)


def pickup_closest_potion(bot: "Bot"):
    return pickup_closest_item(bot, G.POTION_CLASS)


def pickup_closest_boots(bot: "Bot"):
    # TODO: add new class in G for boots
    boot_glyphs = [
        glyph
        for glyph, obj in GLYPH_TO_OBJECT.items()
        if obj["obj_class"] == chr(ItemClasses.ARMOR.value) and obj["obj"].oc_armcat == 4
    ]
    boot_glyphs = frozenset(boot_glyphs)
    return pickup_closest_item(bot, boot_glyphs)


def pickup_closest_horn(bot: "Bot"):
    horn_glyphs = [
        glyph
        for glyph, obj in GLYPH_TO_OBJECT.items()
        if obj["obj_class"] == chr(ItemClasses.TOOLS.value) and obj["obj_description"] == "horn"
    ]
    horn_glyphs = frozenset(horn_glyphs)
    return pickup_closest_item(bot, horn_glyphs)

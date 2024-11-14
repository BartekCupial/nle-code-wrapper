from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.utils.utils import coords


def pickup_items(bot: "Bot"):
    """
    Pickup items on the ground.

    Args:
        bot (Bot): Bot object.

    Returns:
        bool: True if item was picked up, False otherwise.
    """
    item_coords = coords(bot.glyphs, G.OBJECTS)

    if bot.entity.position in item_coords:
        bot.step(A.Command.PICKUP)
        return True
    else:
        return False

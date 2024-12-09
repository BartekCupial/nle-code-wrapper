import numpy as np
from nle import nethack
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.explore import explore_room
from nle_code_wrapper.bot.strategies.goto import get_other_features, goto_closest
from nle_code_wrapper.bot.strategies.pickup import pickup_closest_boots, pickup_closest_potion, pickup_closest_ring
from nle_code_wrapper.bot.strategies.skill_simple import puton_ring, quaff_potion, wear_boots
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import label_dungeon_features, room_detection, save_boolean_array_pillow


def levitate(bot: "Bot"):
    # 1) if we don't have levitation and there is a lava river
    # pickup potion, ring, boots
    if pickup_closest_potion(bot) or pickup_closest_ring(bot) or pickup_closest_boots(bot):
        pass

    # TODO: try different items until levitating
    # 2) use potion, ring, boots to acquire a levitation
    if quaff_potion(bot) or puton_ring(bot) or wear_boots(bot):
        pass

    # 3) return True if we are levitating
    if bot.blstats.prop_mask & nethack.BL_MASK_LEV:
        return True
    else:
        return False


def levitate_over_lava_river(bot: "Bot"):
    # 0) detect lava river
    starting_pos = bot.entity.position
    lava = utils.isin(bot.glyphs, frozenset({SS.S_lava}))
    labels, num_rooms, num_corridors = label_dungeon_features(bot)
    features, num_features = ndimage.label(labels > 0)
    features_lava, num_lava_features = ndimage.label(np.logical_or(labels > 0, lava))

    def f(x):
        return features, num_features

    unvisited_rooms = get_other_features(bot, f)
    if num_features <= num_lava_features:
        return False

    # 2) levitate
    if not levitate(bot):
        return False

    # 3) cross river
    if goto_closest(bot, unvisited_rooms):
        return features[starting_pos] != features[bot.entity.position]

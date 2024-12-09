import numpy as np
from nle import nethack
from nle.nethack import actions as A
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.explore import explore_room
from nle_code_wrapper.bot.strategies.goto import get_other_features, goto_closest
from nle_code_wrapper.bot.strategies.pickup import (
    pickup_closest_boots,
    pickup_closest_horn,
    pickup_closest_potion,
    pickup_closest_ring,
    pickup_closest_wand,
)
from nle_code_wrapper.bot.strategies.skill_simple import puton_ring, quaff_potion, wear_boots
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import label_dungeon_features, room_detection, save_boolean_array_pillow


def detect_lava_river(bot: "Bot"):
    lava = utils.isin(bot.glyphs, frozenset({SS.S_lava}))
    labels, num_rooms, num_corridors = label_dungeon_features(bot)
    features, num_features = ndimage.label(labels > 0)
    features_lava, num_lava_features = ndimage.label(np.logical_or(labels > 0, lava))
    return features, num_features, features_lava, num_lava_features


@strategy
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


@strategy
def levitate_over_lava_river(bot: "Bot"):
    # 2) detect lava river
    starting_pos = bot.entity.position
    features, num_features, features_lava, num_lava_features = detect_lava_river(bot)
    if num_features <= num_lava_features:
        return False

    def f(x):
        return features, num_features

    unvisited_rooms = get_other_features(bot, f)

    # 2) levitate
    if not levitate(bot):
        return False

    # 3) cross river
    if goto_closest(bot, unvisited_rooms):
        return features[starting_pos] != features[bot.entity.position]


def shortest_path_to_the_other_side(bot: "Bot", positions):
    # If no positions, return False
    if len(positions) == 0:
        return False

    # Go to the closest position
    distances = np.sum(np.abs(positions - bot.entity.position), axis=1)
    closest_position = positions[np.argmin(distances)]

    bot.pathfinder.movements.levitating = True
    path = bot.pathfinder.get_path_to(tuple(closest_position))

    return path


def freeze_lava_wand(bot: "Bot"):
    items = bot.inventory["wands"]

    # try with wand of cold
    for item in items:
        if "wand of cold" in item.full_name:
            bot.step(A.Command.ZAP)
            bot.step(item.letter)
            # TODO: compute this generally
            bot.step(A.CompassCardinalDirection.E)
            if "lava cools and solidifies" in bot.message:
                return True

    # if no wand of cold try with random wand
    for item in items:
        bot.step(A.Command.ZAP)
        bot.step(item.letter)
        # TODO: compute this generally
        bot.step(A.CompassCardinalDirection.E)
        if "lava cools and solidifies" in bot.message:
            return True

    return False


def freeze_lava_horn(bot: "Bot"):
    items = bot.inventory["tools"]
    for item in items:
        if "horn" in item.name:
            bot.step(A.Command.APPLY)
            bot.step(item.letter)
            if "Improvise" in bot.message:
                bot.type_text("y")
                if "what direction" in bot.message:
                    # TODO: compute this generally
                    bot.step(A.CompassCardinalDirection.E)
                    if "lava cools and solidifies" in bot.message:
                        return True
    return False


@strategy
def freeze_lava_river(bot: "Bot"):
    # 1) detect lava river
    starting_pos = bot.entity.position
    features, num_features, features_lava, num_lava_features = detect_lava_river(bot)
    if num_features <= num_lava_features:
        return False

    def f(x):
        return features, num_features

    unvisited_rooms = get_other_features(bot, f)

    # 2) pickup stuff
    while pickup_closest_wand(bot) or pickup_closest_horn(bot):
        pass

    # 3) break through lava with freezing
    # imagine that we are levitating to compute path to cross lava
    path = shortest_path_to_the_other_side(bot, unvisited_rooms)
    path = path[1:]  # distard our position

    for point in path:
        if bot.glyphs[tuple(point)] == SS.S_lava:
            freeze_lava_horn(bot) or freeze_lava_wand(bot)
        bot.pathfinder.move(point)

    # 4) return True if we broke through lava
    return features[starting_pos] != features[bot.entity.position]

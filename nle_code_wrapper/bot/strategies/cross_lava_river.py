import numpy as np
from nle import nethack
from nle.nethack import actions as A
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.explore import explore_room
from nle_code_wrapper.bot.strategies.goto import get_other_features, goto_closest
from nle_code_wrapper.bot.strategies.pickup import pickup_boots, pickup_horn, pickup_potion, pickup_ring, pickup_wand
from nle_code_wrapper.bot.strategies.skill_simple import puton_ring, quaff_potion, wear_boots
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import label_dungeon_features, room_detection, save_boolean_array_pillow


def lava_river_detection(bot: "Bot"):
    lava = utils.isin(bot.glyphs, frozenset({SS.S_lava}))
    labels, num_rooms, num_corridors = label_dungeon_features(bot)
    features, num_features = ndimage.label(labels > 0)
    features_lava, num_lava_features = ndimage.label(np.logical_or(labels > 0, lava))
    return features, num_features, features_lava, num_lava_features


@strategy
def acquire_levitation(bot: "Bot"):
    # 1) if we don't have levitation and there is a lava river
    # pickup potion, ring, boots
    if pickup_potion(bot) or pickup_ring(bot) or pickup_boots(bot):
        pass

    # TODO: try different items until levitating
    # 2) use potion, ring, boots to acquire a levitation
    if quaff_potion(bot) or puton_ring(bot) or wear_boots(bot):
        pass

    # 3) return True if we are levitating
    return bot.blstats.prop_mask & nethack.BL_MASK_LEV


@strategy
def cross_lava_river(bot: "Bot"):
    features, num_features, features_lava, num_lava_features = lava_river_detection(bot)
    if num_features <= num_lava_features:
        return False

    def f(x):
        return features, num_features

    unvisited_rooms = get_other_features(bot, f)

    starting_pos = bot.entity.position
    if goto_closest(bot, unvisited_rooms):
        return features[starting_pos] != features[bot.entity.position]


@strategy
def levitate_over_lava_river(bot: "Bot"):
    # 1) detect lava river
    features, num_features, features_lava, num_lava_features = lava_river_detection(bot)
    if num_features <= num_lava_features:
        return False

    # 2) levitate
    if not acquire_levitation(bot):
        return False

    # 3) cross river
    return cross_lava_river(bot)


def shortest_path_to_the_other_side(bot: "Bot", positions):
    # If no positions, return False
    if len(positions) == 0:
        return False

    # Go to the closest position
    distances = np.sum(np.abs(positions - bot.entity.position), axis=1)
    closest_position = positions[np.argmin(distances)]

    # imagine that we are levitating to compute path to cross lava
    bot.pathfinder.movements.levitating = True
    path = bot.pathfinder.get_path_to(tuple(closest_position))

    return path


@strategy
def freeze_lava_wand(bot: "Bot"):
    items = bot.inventory["wands"]

    # First try wands of cold, then any other wands
    wand_priorities = [
        lambda item: "wand of cold" in item.full_name,  # First priority
        lambda item: True,  # Fall back to any wand
    ]

    for priority_check in wand_priorities:
        for item in items:
            if priority_check(item):
                bot.step(A.Command.ZAP)
                bot.step(item.letter)
                # TODO: compute this generally
                bot.step(A.CompassCardinalDirection.E)
                if "lava cools and solidifies" in bot.message:
                    return True

    return False


@strategy
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
    features, num_features, features_lava, num_lava_features = lava_river_detection(bot)
    if num_features <= num_lava_features:
        return False

    def f(x):
        return features, num_features

    unvisited_rooms = get_other_features(bot, f)

    # 2) pickup stuff
    while pickup_wand(bot) or pickup_horn(bot):
        pass

    # 3) break through lava with freezing
    path = shortest_path_to_the_other_side(bot, unvisited_rooms)
    path = path[1:]  # distard our position

    starting_pos = bot.entity.position
    for point in path:
        if bot.glyphs[tuple(point)] == SS.S_lava:
            freeze_lava_horn(bot) or freeze_lava_wand(bot)
        bot.pathfinder.move(point)

    # 4) return True if we broke through lava
    return features[starting_pos] != features[bot.entity.position]

import numpy as np
from nle import nethack
from nle.nethack import actions as A
from nle_utils.glyph import SS, G
from scipy import ndimage

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.explore import explore_room
from nle_code_wrapper.bot.strategies.goto import get_other_features, goto_closest
from nle_code_wrapper.bot.strategies.pickup import pickup_armor, pickup_potion, pickup_ring, pickup_tool, pickup_wand
from nle_code_wrapper.bot.strategies.quaff import quaff_potion
from nle_code_wrapper.bot.strategies.wear import puton_ring, wear_boots
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
    """
    Attempts to acquire levitation status by collecting items and trying them.
    """
    # 1) if we don't have levitation and there is a lava river
    # pickup potion, ring, boots
    if pickup_potion(bot) or pickup_ring(bot) or pickup_armor(bot):
        pass

    # TODO: try different items until levitating
    # 2) use potion, ring, boots to acquire a levitation
    if quaff_potion(bot) or puton_ring(bot) or wear_boots(bot):
        pass

    # 3) return True if we are levitating
    return bot.blstats.prop_mask & nethack.BL_MASK_LEV


def shortest_path_to_the_other_side(bot: "Bot", positions):
    # If no positions, return False
    if len(positions) == 0:
        return False

    # imagine that we are levitating to compute path to cross lava
    lev = bot.movements.levitating
    bot.movements.levitating = True

    # select path which will cross lava (there could be other rooms)
    lava_paths = []
    for pos in positions:
        path = bot.pathfinder.get_path_to(tuple(pos))
        if path is None:
            continue
        if any([bot.glyphs[tuple(point)] == SS.S_lava for point in path if point]):
            lava_paths.append(path)

    bot.movements.levitating = lev

    # return shortest path
    return min(lava_paths, key=len, default=None)


@strategy
def cross_lava_river(bot: "Bot"):
    """
    Attempts to cross a lava river, even if this means burning to death.
    """

    features, num_features, features_lava, num_lava_features = lava_river_detection(bot)
    if num_features <= num_lava_features:
        return False

    def f(x):
        return features, num_features

    unvisited_rooms = get_other_features(bot, f)

    path = shortest_path_to_the_other_side(bot, unvisited_rooms)
    if not path:
        return False
    starting_pos = bot.entity.position
    if bot.pathfinder.goto(tuple(path[-1])):
        return features[starting_pos] != features[bot.entity.position]


@strategy
def levitate_over_lava_river(bot: "Bot"):
    """
    Full lava river crossing strategy by detecting lava, collecting levitation
    items, using them and attempting to levitate over a lava river.
    """
    # 1) detect lava river
    features, num_features, features_lava, num_lava_features = lava_river_detection(bot)
    if num_features <= num_lava_features:
        return False

    # 2) levitate
    if not acquire_levitation(bot):
        return False

    # 3) cross river
    return cross_lava_river(bot)


@strategy
def freeze_lava_wand(bot: "Bot"):
    """
    Attempts to freeze lava using wands from the bot's inventory, pointing eastward.
    """
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
    """
    Attempts to freeze lava using horns from the bot's inventory, pointing eastward.
    """
    items = bot.inventory["tools"]
    for item in items:
        if item.name is not None and "horn" in item.name:
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
def approach_lava_river(bot: "Bot"):
    """
    Navigates the bot to the edge of a detected lava river.
    """
    # 1) detect lava river
    features, num_features, features_lava, num_lava_features = lava_river_detection(bot)
    if num_features <= num_lava_features:
        return False

    def f(x):
        return features, num_features

    unvisited_rooms = get_other_features(bot, f)

    # 2) go to the edge of lava
    path = shortest_path_to_the_other_side(bot, unvisited_rooms)
    if not path:
        return False
    path = path[1:]  # distard our position

    for point in path:
        if bot.glyphs[tuple(point)] == SS.S_lava:
            return True
        bot.pathfinder.move(point)

    return False


@strategy
def freeze_lava_river(bot: "Bot"):
    """
    Full lava river crossing strategy by detecting lava, collecting freezing
    items, approaching lava edge, and attempting to freeze it.
    """
    # 1) detect lava river
    features, num_features, features_lava, num_lava_features = lava_river_detection(bot)
    if num_features <= num_lava_features:
        return False

    def f(x):
        return features, num_features

    unvisited_rooms = get_other_features(bot, f)

    # 2) pickup stuff
    while pickup_wand(bot) or pickup_tool(bot):
        pass

    starting_pos = bot.entity.position
    # 3) appraoch lava
    if approach_lava_river(bot):
        while True:
            # if we can approach lava, we can freeze it
            if approach_lava_river(bot):
                # break through lava with freezing
                freeze_lava_horn(bot) or freeze_lava_wand(bot)
            # no lava in front of us, walk to the other side
            else:
                goto_closest(bot, unvisited_rooms)
                break

    # 4) return True if we broke through lava
    return features[starting_pos] != features[bot.entity.position]

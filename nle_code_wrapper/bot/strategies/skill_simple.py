import re
from typing import Callable, Optional

from nle.nethack import actions as A
from nle_utils.glyph import G
from nle_utils.item import ArmorType

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import Item
from nle_code_wrapper.bot.strategies.goto import goto_glyph
from nle_code_wrapper.bot.strategy import strategy


def remove_if_worn(bot: "Bot", cat: ArmorType) -> Optional[int]:
    """
    Removes armor of the given type if it is currently worn.
    Returns True if removal was attempted, False otherwise.
    """
    for item in bot.inventory["armor"]:
        if item.object.oc_armcat == cat.value and item.is_worn:
            bot.step(A.Command.TAKEOFF)
            bot.step(item.letter)
            return item.letter
    return None


def wear_atype(bot: "Bot", a_type):
    for item in bot.inventory["armor"]:
        if item.object.oc_armcat == a_type.value:
            bot.step(A.Command.WEAR)
            bot.step(item.letter)
            return True
    return False


def wear_if_removed(bot: "Bot", letter: Optional[int]) -> bool:
    if letter is not None:
        bot.step(A.Command.WEAR)
        bot.step(letter)


def wear_func(bot: "Bot", armor_type) -> bool:
    # 1) Take off
    # Handle special prerequisites:
    if armor_type == ArmorType.SUIT:
        # Must take off cloak before wearing a suit
        removed_cloak = remove_if_worn(bot, ArmorType.CLOAK)
    elif armor_type == ArmorType.SHIRT:
        # Must take off suit, then cloak, in that order
        removed_cloak = remove_if_worn(bot, ArmorType.CLOAK)
        removed_suit = remove_if_worn(bot, ArmorType.SUIT)

    # 2) Wear an item of this armor type (if present in inventory)
    ret = wear_atype(bot, armor_type)

    # put on suit and shirt back
    if armor_type == ArmorType.SUIT:
        wear_if_removed(bot, removed_cloak)
    elif armor_type == ArmorType.SHIRT:
        wear_if_removed(bot, removed_suit)
        wear_if_removed(bot, removed_cloak)

    return ret


def wear_suit(bot: "Bot") -> bool:
    """
    Wears SUIT from inventory
    """
    return wear_func(bot, ArmorType.SUIT)


def wear_shield(bot: "Bot") -> bool:
    """
    Wears SHIELD from inventory
    """
    return wear_func(bot, ArmorType.SHIELD)


def wear_helm(bot: "Bot") -> bool:
    """
    Wears SHIELD from inventory
    """
    return wear_func(bot, ArmorType.SHIELD)


def wear_boots(bot: "Bot") -> bool:
    """
    Wears BOOTS from inventory
    """
    return wear_func(bot, ArmorType.BOOTS)


def wear_gloves(bot: "Bot") -> bool:
    """
    Wears GLOVES from inventory
    """
    return wear_func(bot, ArmorType.GLOVES)


def wear_cloak(bot: "Bot") -> bool:
    """
    Wears CLOAK from inventory
    """
    return wear_func(bot, ArmorType.CLOAK)


def wear_shirt(bot: "Bot") -> bool:
    """
    Wears SHIRT from inventory
    """
    return wear_func(bot, ArmorType.SHIRT)


@strategy
def puton_ring(bot: "Bot"):
    """
    Puts on ring from an inventory.
    """
    items = bot.inventory["rings"]
    for item in items:
        bot.step(A.Command.PUTON)
        bot.step(item.letter)
        if "Which ring-finger, Right or Left?" in bot.message:
            bot.type_text("r")
        return True

    return False


@strategy
def quaff_potion(bot: "Bot"):
    """
    Drinks potion from inventory.
    """
    items = bot.inventory["potions"]
    for item in items:
        bot.step(A.Command.QUAFF)
        bot.step(item.letter)
        return True

    return False


def eat_from_inventory(bot: "Bot", item: Item):
    assert item in bot.inventory.items

    bot.step(A.Command.EAT)

    # 1) get out of eating stuff from the floor
    while "; eat it? [ynq]" in bot.message or "; eat one? [ynq]" in bot.message:
        bot.type_text("n")

    # 2) eat from inventory
    if "What do you want to eat?" in bot.message:
        bot.step(item.letter)

        while "Continue eating?" in bot.message:
            bot.type_text("y")

        if (
            "You finish eating" in bot.message
            or "You're finally finished." in bot.message
            or "is delicious!" in bot.message
            or "Ecch - that must have been poisonous!" in bot.message
            or "You seem unaffected by the poison." in bot.message
        ):
            return True

    return False


def eat_from_floor(bot: "Bot", item: Item):
    # TODO: implement items_below_me
    assert item in bot.items_below_me

    bot.step(A.Command.EAT)
    while "; eat it? [ynq]" in bot.message or "; eat one? [ynq]" in bot.message:
        if (
            f"{item.full_name} here; eat it? [ynq]" in bot.message
            or f"{item.full_name} here; eat one? [ynq]" in bot.message
        ):
            bot.type_text("y")

            while "Continue eating?" in bot.message:
                bot.type_text("y")

            if "You finish eating" in bot.message or "You're finally finished." in bot.message:
                return True
        else:
            bot.type_text("n")

    return False


@strategy
def eat_food_inventory(bot: "Bot"):
    """
    Eats food from inventory.
    """
    food_items = [(item.nutrition / item.weight, item) for item in bot.inventory["comestibles"] if item.is_food]

    if food_items:
        food = min(food_items, key=lambda x: x[0])[1]
        return eat_from_inventory(bot, food)

    return False


@strategy
def eat_corpse_inventory(bot: "Bot"):
    """
    Eats corpse from inventory.
    """
    food_items = [(item.nutrition / item.weight, item) for item in bot.inventory["comestibles"] if item.is_corpse]

    if food_items:
        food = min(food_items, key=lambda x: x[0])[1]
        return eat_from_inventory(bot, food)

    return False


@strategy
def eat_corpse_floor(bot: "Bot"):
    """
    Eats corpse from floor.
    """
    bot.step(A.Command.EAT)
    while "; eat it? [ynq]" in bot.message or "; eat one? [ynq]" in bot.message:
        if "corpse" in bot.message:
            bot.type_text("y")

            while "Continue eating?" in bot.message:
                bot.type_text("n")  # prevent choking on food

            if "You finish eating" in bot.message or "You're finally finished." in bot.message:
                return True
        else:
            bot.type_text("n")

    return False

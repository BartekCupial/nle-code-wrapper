from typing import List

from nle.nethack import actions as A

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import ArmorType
from nle_code_wrapper.bot.strategy import strategy


def _simple_takeoff(bot: "Bot", armor_type: ArmorType) -> bool:
    """Base function for simple takeoff operations"""
    item = bot.inventory.worn_armor_by_type[armor_type]
    if item is not None:
        bot.step(A.Command.TAKEOFF)
        bot.step(item.letter)
        return bot.inventory.worn_armor_by_type[armor_type] is None
    return False


def _takeoff_with_dependencies(bot: "Bot", dependencies: List[ArmorType], armor_type: ArmorType) -> bool:
    """Helper for taking off items that require removing other items first"""
    if bot.inventory.worn_armor_by_type[armor_type] is None:
        return False

    # Store letters of items we need to remove first
    temp_items = []

    # Take off dependent items in order
    for dep_type in dependencies:
        item = bot.inventory.worn_armor_by_type[dep_type]
        if item is not None:
            temp_items.append(item.letter)
            bot.step(A.Command.TAKEOFF)
            bot.step(item.letter)

            # Check if dependent item couldn't be taken off
            if bot.inventory.worn_armor_by_type[dep_type] is not None:
                # Put back any items we've already removed
                for letter in reversed(temp_items):
                    bot.step(A.Command.WEAR)
                    bot.step(letter)
                return False

    # Take off target item
    bot.step(A.Command.TAKEOFF)
    bot.step(bot.inventory.worn_armor_by_type[armor_type].letter)

    # Put back dependent items in reverse order
    for letter in reversed(temp_items):
        bot.step(A.Command.WEAR)
        bot.step(letter)

    return bot.inventory.worn_armor_by_type[armor_type] is None


@strategy
def takeoff_shield(bot: "Bot") -> bool:
    return _simple_takeoff(bot, ArmorType.SHIELD)


@strategy
def takeoff_helm(bot: "Bot") -> bool:
    return _simple_takeoff(bot, ArmorType.HELM)


@strategy
def takeoff_boots(bot: "Bot") -> bool:
    return _simple_takeoff(bot, ArmorType.BOOTS)


@strategy
def takeoff_gloves(bot: "Bot") -> bool:
    return _simple_takeoff(bot, ArmorType.GLOVES)


@strategy
def takeoff_cloak(bot: "Bot") -> bool:
    return _simple_takeoff(bot, ArmorType.CLOAK)


@strategy
def takeoff_suit(bot: "Bot") -> bool:
    return _takeoff_with_dependencies(
        bot,
        dependencies=[ArmorType.CLOAK],
        armor_type=ArmorType.SUIT,
    )


@strategy
def takeoff_shirt(bot: "Bot") -> bool:
    return _takeoff_with_dependencies(
        bot,
        dependencies=[ArmorType.CLOAK, ArmorType.SUIT],
        armor_type=ArmorType.SHIRT,
    )

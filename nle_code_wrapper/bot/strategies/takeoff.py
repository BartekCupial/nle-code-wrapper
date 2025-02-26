from typing import List

from nle.nethack import actions as A

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import ArmorClass
from nle_code_wrapper.bot.strategy import strategy


def _simple_takeoff(bot: "Bot", armor_class: ArmorClass) -> bool:
    """Base function for simple takeoff operations"""
    item = bot.inventory.worn_armor_by_type[armor_class]
    if item is not None:
        bot.step(A.Command.TAKEOFF)
        bot.step(item.letter)
        return bot.inventory.worn_armor_by_type[armor_class] is None
    return False


def _takeoff_with_dependencies(bot: "Bot", dependencies: List[ArmorClass], armor_class: ArmorClass) -> bool:
    """Helper for taking off items that require removing other items first"""
    if bot.inventory.worn_armor_by_type[armor_class] is None:
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
    bot.step(bot.inventory.worn_armor_by_type[armor_class].letter)

    # Put back dependent items in reverse order
    for letter in reversed(temp_items):
        bot.step(A.Command.WEAR)
        bot.step(letter)

    return bot.inventory.worn_armor_by_type[armor_class] is None


@strategy
def takeoff_shield(bot: "Bot") -> bool:
    return _simple_takeoff(bot, ArmorClass.SHIELD)


@strategy
def takeoff_helm(bot: "Bot") -> bool:
    return _simple_takeoff(bot, ArmorClass.HELM)


@strategy
def takeoff_boots(bot: "Bot") -> bool:
    return _simple_takeoff(bot, ArmorClass.BOOTS)


@strategy
def takeoff_gloves(bot: "Bot") -> bool:
    return _simple_takeoff(bot, ArmorClass.GLOVES)


@strategy
def takeoff_cloak(bot: "Bot") -> bool:
    return _simple_takeoff(bot, ArmorClass.CLOAK)


@strategy
def takeoff_suit(bot: "Bot") -> bool:
    return _takeoff_with_dependencies(
        bot,
        dependencies=[ArmorClass.CLOAK],
        armor_class=ArmorClass.SUIT,
    )


@strategy
def takeoff_shirt(bot: "Bot") -> bool:
    return _takeoff_with_dependencies(
        bot,
        dependencies=[ArmorClass.CLOAK, ArmorClass.SUIT],
        armor_class=ArmorClass.SHIRT,
    )

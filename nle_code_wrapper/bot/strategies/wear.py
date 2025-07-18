from typing import List, Optional

from nle.nethack import actions as A

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import ArmorClass, Item, ItemBeatitude
from nle_code_wrapper.bot.strategy import strategy


def _get_best_armor(bot: "Bot", armor_class: ArmorClass) -> Optional[Item]:
    """Selects best armor item by arm_bonus for given type"""
    best = None
    best_unknown = None

    for item in bot.inventory["armor"]:
        if item.armor_class == armor_class:
            if item.beatitude == ItemBeatitude.CURSED:
                continue
            elif item.beatitude == ItemBeatitude.UNKNOWN:
                # Track best unknown item separately
                if best_unknown is None or item.arm_bonus > best_unknown.arm_bonus:
                    best_unknown = item
            else:
                # For BLESSED / UNCURSED items, update if better
                if best is None or item.arm_bonus > best.arm_bonus:
                    best = item

    # Return best blessed / uncursed item if found, otherwise return best non-cursed item
    return best if best is not None else best_unknown


def _simple_wear(bot: "Bot", armor_class) -> bool:
    """Base function for simple wear operations"""
    best_item = _get_best_armor(bot, armor_class)
    if best_item is None or best_item.equipped:
        return False

    bot.step(A.Command.WEAR)
    bot.step(best_item.letter)

    return bot.inventory.worn_armor_by_type[armor_class] is not None


def _wear_with_dependencies(bot: "Bot", dependencies: List[ArmorClass], armor_class: ArmorClass) -> bool:
    """Helper for wearing items that require removing other items first"""
    best_item = _get_best_armor(bot, armor_class)
    if best_item is None or best_item.equipped:
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

    # Wear target item
    bot.step(A.Command.WEAR)
    bot.step(best_item.letter)

    # Put back dependent items in reverse order
    for letter in reversed(temp_items):
        bot.step(A.Command.WEAR)
        bot.step(letter)

    return bot.inventory.worn_armor_by_type[armor_class] is not None


@strategy
def wear_shield(bot: "Bot") -> bool:
    """Wears a shield from inventory."""
    return _simple_wear(bot, ArmorClass.SHIELD)


@strategy
def wear_helm(bot: "Bot") -> bool:
    """Wears a helm from inventory."""
    return _simple_wear(bot, ArmorClass.HELM)


@strategy
def wear_boots(bot: "Bot") -> bool:
    """Wears boots from inventory."""
    return _simple_wear(bot, ArmorClass.BOOTS)


@strategy
def wear_gloves(bot: "Bot") -> bool:
    """Wears gloves from inventory."""
    return _simple_wear(bot, ArmorClass.GLOVES)


@strategy
def wear_cloak(bot: "Bot") -> bool:
    """Wears a cloak from inventory."""
    return _simple_wear(bot, ArmorClass.CLOAK)


@strategy
def wear_suit(bot: "Bot") -> bool:
    """Wears a suit from inventory."""
    # Note: To wear a suit, we need to remove the cloak first
    return _wear_with_dependencies(
        bot,
        dependencies=[ArmorClass.CLOAK],
        armor_class=ArmorClass.SUIT,
    )


@strategy
def wear_shirt(bot: "Bot") -> bool:
    """Wears a shirt from inventory."""
    # To wear a shirt, we need to remove both cloak and suit
    return _wear_with_dependencies(
        bot,
        dependencies=[ArmorClass.CLOAK, ArmorClass.SUIT],
        armor_class=ArmorClass.SHIRT,
    )


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
def puton_amulet(bot: "Bot"):
    """
    Puts on amulet from an inventory.
    """
    items = bot.inventory["amulets"]
    for item in items:
        bot.step(A.Command.PUTON)
        bot.step(item.letter)
        return True

    return False

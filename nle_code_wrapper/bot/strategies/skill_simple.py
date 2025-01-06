from typing import Callable

from nle.nethack import actions as A
from nle_utils.item import ArmorType

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


def remove_armor_if_worn(bot: "Bot", cat: ArmorType) -> bool:
    """
    Removes armor of the given type if it is currently worn.
    Returns True if removal was attempted, False otherwise.
    """
    for item in bot.inventory["armor"]:
        if item.object.oc_armcat == cat.value and item.is_worn:
            bot.step(A.Command.REMOVE)
            bot.step(item.letter)
            return True
    return False


def create_wear_function(armor_type: ArmorType) -> Callable[["Bot"], bool]:
    """Dynamically create a function that wears a given armor type."""

    def wear_func(bot: "Bot", a_type=armor_type) -> bool:
        # 1) Take off

        # Handle special prerequisites:
        if a_type == ArmorType.SUIT:
            # Must take off cloak before wearing a suit
            remove_armor_if_worn(bot, ArmorType.CLOAK)

        elif a_type == ArmorType.SHIRT:
            # Must take off suit, then cloak, in that order
            remove_armor_if_worn(bot, ArmorType.SUIT)
            remove_armor_if_worn(bot, ArmorType.CLOAK)

        # 2) Wear an item of this armor type (if present in inventory)
        for item in bot.inventory["armor"]:
            if item.object.oc_armcat == a_type.value:
                bot.step(A.Command.WEAR)
                bot.step(item.letter)
                return True

        return False

    wear_func.__name__ = f"wear_{armor_type.name.lower()}"
    wear_func.__doc__ = f"Wears {armor_type.name.lower()} from inventory."
    return wear_func


def wear_suit(bot: "Bot") -> bool:
    ...


def wear_shield(bot: "Bot") -> bool:
    ...


def wear_helm(bot: "Bot") -> bool:
    ...


def wear_boots(bot: "Bot") -> bool:
    ...


def wear_gloves(bot: "Bot") -> bool:
    ...


def wear_cloak(bot: "Bot") -> bool:
    ...


def wear_shirt(bot: "Bot") -> bool:
    ...


for a_type in ArmorType:
    globals()[f"wear_{a_type.name.lower()}"] = strategy(create_wear_function(a_type))


@strategy
def puton_ring(bot: "Bot"):
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
    items = bot.inventory["potions"]
    for item in items:
        bot.step(A.Command.QUAFF)
        bot.step(item.letter)
        return True

    return False

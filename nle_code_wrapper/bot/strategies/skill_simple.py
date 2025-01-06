from typing import Callable, Optional

from nle.nethack import actions as A
from nle_utils.item import ArmorType

from nle_code_wrapper.bot import Bot
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


def create_wear_function(armor_type: ArmorType) -> Callable[["Bot"], bool]:
    """Dynamically create a function that wears a given armor type."""

    # TODO: fix and write tests for wearing
    def wear_func(bot: "Bot", a_type=armor_type) -> bool:
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
        ret = wear_atype(bot, a_type)

        # put on suit and shirt back
        if armor_type == ArmorType.SUIT:
            wear_if_removed(bot, removed_cloak)
        elif armor_type == ArmorType.SHIRT:
            wear_if_removed(bot, removed_suit)
            wear_if_removed(bot, removed_cloak)

        return ret

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

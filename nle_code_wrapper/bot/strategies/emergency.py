from typing import List, Optional, Tuple

from nle.nethack import actions as A

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.inventory.properties import ItemBeatitude
from nle_code_wrapper.bot.strategy import repeat, strategy


def use_item(
    bot: "Bot", items: List[str], item_category: str, command: A.Command, beatitude: Optional[List[str]] = None
) -> bool:
    """
    Use an item from the inventory by its letter.

    Args:
        bot (Bot): The bot instance.
        items (List[str]): List of items to use (e.g., ["carrot"]).
        item_category (str): The category of the items (e.g., "food", "potions").
        command (A.Command): The command to execute (e.g., APPLY, QUAFF).
        beatitude (Optional[List[str]]): List of beatitudes to filter (e.g., ["blessed", "uncursed"]).

    Returns:
        bool: True if an item was used, False otherwise.
    """
    items = [
        item
        for item in bot.inventory[item_category]
        if any(food in item.name for food in items) and (not beatitude or any([item.beatitude == b for b in beatitude]))
    ]

    for item in items:
        bot.step(command)
        bot.step(item)
        return True

    return False


def eat_carrot(bot: "Bot"):
    """
    Eat a carrot to cure blindness.
    """
    return use_item(bot, ["carrot"], "comestibles", A.Command.EAT)


def eat_lizard_corpse(bot: "Bot"):
    """
    Eat a lizard corpse to cure stoning.
    """
    return use_item(bot, ["lizard corpse"], "comestibles", A.Command.EAT)


def eat_eucalyptus(bot: "Bot"):
    """
    Eat eucalyptus to cure food poisoning or termill.
    """
    return use_item(
        bot,
        ["eucalyptus"],
        "comestibles",
        A.Command.EAT,
        [ItemBeatitude.BLESSED, ItemBeatitude.UNCURSED, ItemBeatitude.UNKNOWN],
    )


def eat_spring_of_wolfsbane(bot: "Bot"):
    """
    Eat a spring of wolfsbane to cure lycanthropy.
    """
    return use_item(bot, ["wolfsbane"], "comestibles", A.Command.EAT)


def apply_unicorn_horn(bot: "Bot"):
    """
    Apply a unicorn horn to cure lycanthropy or confusion.
    """
    return use_item(
        bot,
        ["unicorn horn"],
        "tools",
        A.Command.APPLY,
        [ItemBeatitude.BLESSED, ItemBeatitude.UNCURSED, ItemBeatitude.UNKNOWN],
    )


def apply_potion_of_oil(bot: "Bot"):
    """
    Apply a potion of oil to light it (or snuff it out).
    """
    return use_item(bot, ["oil"], "potions", A.Command.APPLY)


def throw_potion_of_oil(bot: "Bot"):
    # TODO:
    pass


def read_scroll_of_fire(bot: "Bot"):
    """
    Read a scroll of fire to cure slime.
    """
    return use_item(bot, ["fire"], "scrolls", A.Command.READ)


def quaff_healing_potion(bot: "Bot"):
    """
    Quaff a healing potion to restore health.
    """
    return use_item(bot, ["healing", "extra healing", "full healing"], "potions", A.Command.QUAFF)


def quaff_blessed_healing_potion(bot: "Bot"):
    """
    Quaff a blessed healing potion to restore health.
    """
    return use_item(bot, ["healing"], "potions", A.Command.QUAFF, [ItemBeatitude.BLESSED])


def quaff_noncursed_extra_healing_potion(bot: "Bot"):
    """
    Quaff a non-cursed extra healing potion to restore health.
    """
    return use_item(
        bot,
        ["extra healing", "full healing"],
        "potions",
        A.Command.QUAFF,
        [ItemBeatitude.BLESSED, ItemBeatitude.UNCURSED, ItemBeatitude.UNKNOWN],
    )


def quaff_fruit_juice(bot: "Bot"):
    """
    Quaff fruit juice to restore health and cure hunger.
    """
    return use_item(bot, ["fruit juice"], "potions", A.Command.QUAFF)


def quaff_acid_potion(bot: "Bot"):
    """
    Quaff an acid potion to cure stoning.
    """
    return use_item(bot, ["acid"], "potions", A.Command.QUAFF)


def quaff_holy_water(bot: "Bot"):
    """
    Quaff holy water to cure food poisoning or termill.
    """
    return use_item(bot, ["water"], "potions", A.Command.QUAFF, [ItemBeatitude.BLESSED])


def cast_healing(bot: "Bot"):
    return bot.cast("healing", direction=(0, 0), fail=30.0)


def cast_cure_blindness(bot: "Bot"):
    return bot.cast("cure blindness", direction=(0, 0), fail=30.0)


def cast_extra_healing(bot: "Bot"):
    return bot.cast("extra healing", direction=(0, 0), fail=30.0)


def cast_stone_to_flesh(bot: "Bot"):
    return bot.cast("stone to flesh", direction=(0, 0), fail=30.0)


def cast_cure_sickness(bot: "Bot"):
    # check if 100% chance
    bot.cast("cure sickness", direction=(0, 0), fail=0.0)


def zap_yourself_wand_of_fire(bot: "Bot"):
    # TODO:
    pass


def wait_it_out(bot: "Bot", status_name: str):
    status = getattr(bot, status_name)
    while status:
        bot.wait()
        status = getattr(bot, status_name)

    return True


@strategy
def emergency_pray(bot: "Bot") -> bool:
    """
    Attempt to pray if the bot is in an emergency situation. Will not pray if pray timeout is active.
    """
    return bot.safely_pray()


@strategy
def emergency_eat(bot: "Bot"):
    """
    Eat fruit juice if available to satisfy hunger. Use in emergencies when weak from hunger.
    """

    items = [item for item in bot.inventory["potions"] if any(pot in item.name for pot in ["fruit juice"])]

    if items:
        potion = items[0]
        bot.step(A.Command.QUAFF)
        bot.step(potion.letter)

        return True
    else:
        return False


@strategy
def emergency_heal(bot: "Bot"):
    return quaff_healing_potion(bot)


@strategy
def cure_disease(bot: "Bot"):
    """
    Attempt to cure: lycanthropy, stoning, sliming, food poisoning, sickness, hallucination, blindness, stunning, confusion, strangulation, deaf
    """
    # lycanthropy
    if bot.character.is_lycanthrope:
        if eat_spring_of_wolfsbane(bot):
            return True
        elif quaff_holy_water(bot):
            return True
        elif bot.safely_pray():
            return True

    # stoning
    elif bot.stone:
        if eat_lizard_corpse(bot):
            return True
        elif quaff_acid_potion(bot):
            return True
        elif cast_stone_to_flesh(bot):
            return True
        elif bot.safely_pray():
            return True

    # sliming
    elif bot.slime:
        if read_scroll_of_fire(bot):
            return True
        elif zap_yourself_wand_of_fire(bot):
            return True
        # we have to be caught in the explosion from a lit potion of oil
        elif apply_potion_of_oil(bot):
            if throw_potion_of_oil(bot):
                return True
        elif cast_cure_sickness(bot):
            return True
        elif bot.safely_pray():
            return True

    # food poisoning or sickness
    elif bot.foodpois or bot.termill:
        if apply_unicorn_horn(bot):
            return True
        elif quaff_blessed_healing_potion(bot):
            return True
        elif quaff_noncursed_extra_healing_potion(bot):
            return True
        elif quaff_holy_water(bot):
            return True
        elif bot.safely_pray():
            return True
        elif cast_cure_sickness(bot):
            return True
        elif eat_eucalyptus(bot):
            return True

    # hallucination
    elif bot.hallu:
        if apply_unicorn_horn(bot):
            return True
        else:
            return wait_it_out(bot, "hallu")

    # blindness
    elif bot.blind:
        if apply_unicorn_horn(bot):
            return True
        elif eat_carrot(bot):
            return True
        elif cast_cure_blindness(bot):
            return True
        elif cast_extra_healing(bot):
            return True
        elif quaff_healing_potion(bot):
            return True
        else:
            return wait_it_out(bot, "blind")

    # stun or confusion
    elif bot.stun or bot.conf:
        if apply_unicorn_horn(bot):
            return True

        if bot.stun:
            return wait_it_out(bot, "stun")
        elif bot.conf:
            return wait_it_out(bot, "confused")

    # strangulation
    elif bot.strngl:
        # TODO: if amulet of strangulation we should try to pray and then remove it
        # are there any other forms of strangling?
        pass

    # deaf
    elif bot.deaf:
        # this does nothing continue
        pass

    return False

from nle.nethack import actions as A

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import Item
from nle_code_wrapper.bot.strategy import strategy


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

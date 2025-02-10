import re

from nle.nethack import actions as A

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import Item, ItemCategory
from nle_code_wrapper.bot.strategy import strategy


def eat_from_inventory(bot: "Bot", item: Item):
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
    bot.step(A.Command.EAT)
    while "; eat it? [ynq]" in bot.message or "; eat one? [ynq]" in bot.message:
        if str(item) in bot.message:
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
    Eats corpse from floor directly below us.
    """
    bot.step(A.Command.LOOK)

    # only one item
    if match := re.search(r"You see here(.*?)\.", bot.message):
        text = match.group(1).strip()
        properties = bot.inventory.item_parser(text)
        item = Item(
            text=text,
            item_class=bot.inventory_mangager.item_database.get(properties["name"]),
            **properties,
        )
        if item.item_category == ItemCategory.CORPSE:
            return eat_from_floor(bot, item)

    # multiple items
    elif match := re.search(r"Things that are here:(.*?)(?=\n|$)(.*)", bot.message, re.DOTALL):
        items = []
        lines = match.group(2).strip().split("\n")
        for line in lines:
            properties = bot.inventory.item_parser(line)
            item = Item(
                text=line,
                item_class=bot.inventory_mangager.item_database.get(properties["name"]),
                **properties,
            )
            items.append(item)

        # check if there is an item we would like to eat
        if corpses := [item for item in items if item.item_category == ItemCategory.CORPSE]:
            # top corpse will be the most fresh
            return eat_from_floor(bot, corpses[0])

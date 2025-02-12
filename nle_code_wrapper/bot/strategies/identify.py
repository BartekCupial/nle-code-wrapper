import re

from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.inventory import NAME_TO_GLYPHS, Item
from nle_code_wrapper.bot.strategy import strategy


def determine_possible_wands(bot, item):
    wand_regex = "[a-zA-Z ]+"
    floor_regex = "[a-zA-Z]+"
    mapping = {
        f"The engraving on the {floor_regex} vanishes!": ["cancellation", "teleportation", "make invisible"],
        # TODO?: cold,  # (if the existing engraving is a burned one)
        "A few ice cubes drop from the wand.": ["cold"],
        f"The bugs on the {floor_regex} stop moving": ["death", "sleep"],
        f"This {wand_regex} is a wand of digging!": ["digging"],
        "Gravel flies up from the floor!": ["digging"],
        f"This {wand_regex} is a wand of fire!": ["fire"],
        "Lightning arcs from the wand.  You are blinded by the flash!": ["lighting"],
        f"This {wand_regex} is a wand of lightning!": ["lightning"],
        "You burn into the floor with a wand of lightning.": ["lightning"],
        f"The {floor_regex} is riddled by bullet holes!": ["magic missile"],
        "The engraving now reads:": ["polymorph"],
        f"The bugs on the {floor_regex} slow down!": ["slow monster"],
        f"The bugs on the {floor_regex} speed up!": ["speed monster"],
        "The wand unsuccessfully fights your attempt to write!": ["striking"],
        # activated effects:
        "A lit field surrounds you!": ["light"],
        "You may wish for an object.": ["wishing"],
        "You feel self-knowledgeable...": ["enlightenment"],  # TODO: parse the effect
        "For what do you wish?": ["wishing"],  # TODO: parse the effect
        # TODO: "The wand is too worn out to engrave.": [None],  # wand is exhausted
    }

    for msg, wand_types in mapping.items():
        res = re.findall(msg, bot.message)
        if len(res) > 0:
            assert len(res) == 1
            return [NAME_TO_GLYPHS[f"wand of {wand}"] for wand in wand_types]

    # TODO: "wand is cancelled (x:-1)" ?
    # TODO: "secret door detection self-identifies if secrets are detected" ?

    res = re.findall(f"Your {wand_regex} suddenly explodes!", bot.message)
    if len(res) > 0:
        assert len(res) == 1
        return None

    res = re.findall("The wand is too worn out to engrave.", bot.message)
    if len(res) > 0:
        assert len(res) == 1
        # TODO: set number of charges
        return None

    return [
        NAME_TO_GLYPHS[f"wand of {wand}"]
        for wand in ["locking", "opening", "probing", "undead turning", "nothing", "secret door detection"]
    ]


def engrave_single_wand(bot, item):
    """Returns possible objects or None if current tile not suitable for identification."""
    bot.step(A.Command.LOOK)
    if "You see no objects here." not in bot.message:
        return None

    def engrave_fingertips(bot):
        if "What do you want to write with?" not in bot.message:
            return False
        bot.type_text("-")

        if "Do you want to add to the current engraving?" in bot.message:
            bot.type_text("n")

            if "You cannot wipe out the message that is burned into the floor here." in bot.message:
                return False

        if "What do you want to write in the dust here?" in bot.message:
            bot.type_text("x")
            if "What do you want to write in the dust here?" in bot.message:
                bot.type_text("\r")
                return True

        return False

    for _ in range(5):
        # write 'x' with finger in the dust
        bot.step(A.Command.ENGRAVE)

        if not engrave_fingertips(bot):
            return None

        # this is usually true, but something unrelated like: "You hear crashing rock." may happen
        # assert msg().strip() in '', msg()

        # check if the written 'x' is visible when looking
        bot.step(A.Command.LOOK)
        if "Something is written here in the dust." in bot.message and 'You read: "x"' in bot.message:
            break
        else:
            # this is usually true, but something unrelated like:
            #   "There is a doorway here.  Something is written here in the dust. You read: "4".
            #    You see here a giant rat corpse."
            # may happen
            return None
    else:
        assert False, bot.message

    # try engraving with the wand
    bot.step(A.Command.ENGRAVE)

    def engrave_wand(bot, item):
        if "What do you want to write with?" in bot.message:
            bot.step(item.letter)
        else:
            return False

        skip_write_prompts = [
            "You burn into the floor with a wand of lightning.",
            "The engraving on the floor vanishes!",
            "You engrave in the floor with a wand of digging.",
            "You burn into the floor with a wand of fire.",
            "A lit field surrounds you!",
            "You feel self-knowledgeable...",
            "For what do you wish?",
        ]

        if any(prompt in bot.message for prompt in skip_write_prompts):
            return True

        # Handle different "add to existing" prompts
        add_prompts = [
            "Do you want to add to the current engraving",
            "Do you want to add to the writing",
            "Do you want to add to the weird writing",
            "Do you want to add to the epitaph",
            "Do you want to add to the text",
            "Do you want to add to the graffiti",
            "Do you want to add to the scrawl",
        ]

        if any(prompt in bot.message for prompt in add_prompts):
            bot.type_text("y")

        if any(prompt in bot.message for prompt in skip_write_prompts):
            return True

        # Handle different writing prompts
        write_prompts = [
            "What do you want to add to the writing in the dust",
            "What do you want to add to the writing in the frost",
            "What do you want to add to the engraving",
            "What do you want to add to the weird writing",
            "What do you want to add to the epitaph",
            "What do you want to add to the text",
            "What do you want to add to the graffiti",
            "What do you want to add to the scrawl",
            "What do you want to write",
        ]

        if any(prompt in bot.message for prompt in write_prompts):
            bot.type_text("x")  # or whatever text you want to engrave
            bot.type_text("\r")

        return True

    if not engrave_wand(bot, item):
        return None

    possible_wand_types = determine_possible_wands(bot, item)

    # if we had a wand like a wand of digging or lightning it will autoidentify before we engrave
    # then we need to skip engraving for the `determine_possible_wands` to work
    # TODO: currently we skip everything including wishing, and message for wand of enlightement
    # instead we should get out of this function and let the bot act
    while bot.in_getlin or bot.in_yn_function or bot.xwaitingforspace:
        bot.step(A.Command.ESC)

    return possible_wand_types


@strategy
def engrave_identify(bot: "Bot"):
    if bot.poly:
        return False  # TODO: only for handless monsters (which cannot write)

    if bot.blind or bot.lev:
        return False

    if bot.current_level.objects[bot.entity.position] not in G.FLOOR:
        return False

    for item in bot.inventory["wands"]:
        if item.is_identified:
            continue
        if item.item_class.engraved:
            continue

        appearance = item.item_class
        wand_types = engrave_single_wand(bot, item)

        if wand_types is None:
            # there is a problem with engraving on this tile
            continue

        bot.inventory_mangager.item_database.update_item_candidates(appearance, wand_types)
        bot.inventory_mangager.item_database[appearance.name].engraved = True

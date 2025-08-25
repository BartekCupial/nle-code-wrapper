from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategies.goto import goto_glyph
from nle_code_wrapper.bot.strategy import strategy


@strategy
def dip_for_excalibur(bot: "Bot"):
    """Dip long sword into the fountain to get the Excalibur."""

    def excalibur_candidate():
        for item in bot.inventory["weapons"]:
            if "Excalibur" in item.name:
                return None

            if item.name == "long sword":
                return item
        return None

    item = excalibur_candidate()
    if item is None:
        return False

    if not goto_glyph(bot, G.FOUNTAIN):
        return False

    i = 0
    while True:
        bot.step(A.Command.DIP)
        if "What do you want to dip?" in bot.message:
            bot.step(item.letter)

            if "into the fountain?" in bot.message:
                bot.type_text("y")

                # success we have excalibur
                if "As the hand retreats, the fountain disappears!" in bot.message:
                    return True

                elif "fountain dries up!" in bot.message:
                    return False

            else:
                # something went wrong, for example fouintain dried up
                return False

        i += 1
        if i > 10:
            return False

from nle.nethack import actions as A

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


def engrave(bot: "Bot", text: str):
    """
    Engraves a given text using the bot.
    Parameters:
    bot (Bot): The bot instance that will perform the engraving.
    text (str): The text to be engraved.
    The function performs the following steps:
    1. Sends the ENGRAVE command to the bot.
    2. Checks if the bot prompts for a writing tool. If not, it cancels the operation.
    3. Selects fingertips as the writing tool.
    4. If the bot asks whether to add to the current engraving, it responds with 'n' and exits.
    5. Checks if the bot prompts for the text to be written. If not, it cancels the operation.
    6. Sends the text to be engraved to the bot.
    """

    bot.step(A.Command.ENGRAVE)

    if "What do you want to write with?" not in bot.message:
        bot.step(A.Command.ESC)
        return False

    # write with fingertips
    bot.type_text("-")

    if "Do you want to add to the current engraving?" in bot.message:
        bot.type_text("n")

    if "What do you want to write in the dust here?" not in bot.message:
        bot.step(A.Command.ESC)
        return False

    bot.type_text(text)
    return True


@strategy
def engrave_elbereth(bot: "Bot"):
    engrave(bot, "Elbereth")

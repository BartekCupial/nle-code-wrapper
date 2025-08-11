from nle.nethack import actions as A

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def yes(bot: "Bot") -> bool:
    """
    Answer 'yes' to a question.
    """
    bot.type_text("y")
    return True


@strategy
def no(bot: "Bot") -> bool:
    """
    Answer 'no' to a question.
    """
    bot.type_text("n")
    return True


@strategy
def cancel(bot: "Bot") -> bool:
    """
    Cancel the current prompt (ESC).
    """
    bot.step(A.Command.ESC)
    return True


@strategy
def more(bot: "Bot") -> bool:
    """
    Advance through text prompts (MORE).
    """
    bot.step(A.MiscAction.MORE)
    return True

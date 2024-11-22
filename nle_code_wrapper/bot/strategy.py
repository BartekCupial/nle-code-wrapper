from functools import wraps

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.exceptions import BotFinished


def strategy(func):
    """
    A decorator that increments the bot's strategy_step attribute before executing the function.

    Args:
        func: The function to be decorated

    Returns:
        wrapper: The wrapped function that increments strategy_step before execution
    """

    @wraps(func)
    def wrapper(bot: "Bot", *args, **kwargs):
        bot.strategy_steps += 1

        if bot.strategy_steps >= bot.max_strategy_steps:
            bot.truncated = True
            raise BotFinished

        return func(bot, *args, **kwargs)

    return wrapper

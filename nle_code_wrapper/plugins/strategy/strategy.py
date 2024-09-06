from functools import wraps
from typing import TYPE_CHECKING, Callable, Generator

from nle_code_wrapper.bot.exceptions import BotPanic

if TYPE_CHECKING:
    from nle_code_wrapper.bot.bot import Bot


class StrategyManager:
    def __init__(self, bot: "Bot"):
        self.bot = bot
        self.strategies = []
        self.panics = []

    def infinite_iterator(self, generator):
        iterator = iter(generator())
        while True:
            try:
                data = next(iterator)
            except StopIteration:
                iterator = iter(generator())
                data = next(iterator)
            yield data

    def strategy(self, func: Callable[["Bot"], Generator]):
        @wraps(func)
        def wrapper():
            return func(self.bot)

        self.strategies.append(self.infinite_iterator(wrapper))
        return wrapper

    def run_strategies(self):
        while True:
            for strategy in self.strategies:
                try:
                    next(strategy)
                except BotPanic:
                    # for now just go to the next strategy when bot panics
                    pass

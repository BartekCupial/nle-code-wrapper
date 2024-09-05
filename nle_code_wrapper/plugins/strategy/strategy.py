from functools import wraps
from typing import TYPE_CHECKING, Callable, Generator

if TYPE_CHECKING:
    from nle_code_wrapper.bot.bot import Bot


class StrategyManager:
    def __init__(self, bot: "Bot"):
        self.bot = bot
        self.strategies = []

    def strategy(self, func: Callable[["Bot"], Generator]):
        @wraps(func)
        def wrapper():
            return func(self.bot)

        self.strategies.append(wrapper)
        return wrapper

    def run(self):
        while True:
            for strategy in self.strategies:
                yield from strategy()

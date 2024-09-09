from typing import TYPE_CHECKING, Callable, Generator

if TYPE_CHECKING:
    from nle_code_wrapper.bot.bot import Bot


class StrategyManager:
    def __init__(self, bot: "Bot"):
        self.bot = bot

        self.strategies = []
        self.panics = []

    def strategy(self, func: Callable[["Bot"], Generator]):
        self.strategies.append(func)

    def panic(self, func: Callable[["Bot"], Generator]):
        self.panics.append(func(self.bot))

    def run_strategies(self):
        init_strategy = []
        for strategy in self.strategies:
            init_strategy.append(strategy(self.bot))

        while True:
            for strategy in init_strategy:
                strategy()

    def check_panics(self):
        for panic in self.panics:
            panic()

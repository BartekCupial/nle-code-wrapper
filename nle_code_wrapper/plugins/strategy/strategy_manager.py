from functools import wraps
from typing import TYPE_CHECKING, Callable, Generator

from nle_code_wrapper.bot.exceptions import BotPanic

if TYPE_CHECKING:
    from nle_code_wrapper.bot.bot import Bot


class StrategyManager:
    def __init__(self, bot: "Bot"):
        self.bot = bot

        self.strategies = {}
        self.panics = {}

        self.strategy_generators = {}
        self.panic_generators = {}

    def strategy(self, func: Callable[["Bot"], Generator]):
        @wraps(func)
        def wrapper():
            return func(self.bot)

        self.strategies[wrapper.__name__] = wrapper
        return wrapper

    def panic(self, func: Callable[["Bot"], Generator]):
        @wraps(func)
        def wrapper():
            return func(self.bot)

        self.panics[wrapper.__name__] = wrapper
        return wrapper

    def run_strategy(self, strategy_name):
        strategy_func = self.strategies[strategy_name]
        try:
            if strategy_name not in self.strategy_generators:
                self.strategy_generators[strategy_name] = strategy_func()

            # print(f"Running strategy: {strategy_name}")
            ret = next(self.strategy_generators[strategy_name])
            return ret
        except StopIteration:
            # Reset the generator if it's exhausted
            self.strategy_generators[strategy_name] = strategy_func()
        except BotPanic as e:
            # TODO: optionally print panic messages
            # print(f"Panic in strategy {strategy_name}: {e}")
            # Reset the generator after a panic
            self.strategy_generators[strategy_name] = strategy_func()

        return False

    def run_strategies(self):
        while True:
            for strategy_name in self.strategies.keys():
                self.run_strategy(strategy_name)

    def check_panics(self):
        for panic_name, panic_func in self.panics.items():
            try:
                if panic_name not in self.panic_generators:
                    self.panic_generators[panic_name] = panic_func()

                if msg := next(self.panic_generators[panic_name]):
                    raise BotPanic(f"Panic {panic_name}: {msg}")
            except StopIteration:
                # Reset the generator if it's exhausted
                self.panic_generators[panic_name] = panic_func()

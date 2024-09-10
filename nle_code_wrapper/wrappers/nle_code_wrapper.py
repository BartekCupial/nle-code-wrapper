import importlib
from typing import List

import gymnasium as gym

from nle_code_wrapper.bot import Bot


def get_function_by_name(module_name, function_name):
    try:
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        if callable(function):
            return function
        else:
            raise AttributeError(f"{function_name} is not a callable function in {module_name}")
    except ImportError:
        raise ImportError(f"Module {module_name} not found")
    except AttributeError:
        raise AttributeError(f"Function {function_name} not found in module {module_name}")


class NLECodeWrapper(gym.Wrapper):
    def __init__(self, env, strategies: List[str]):
        super().__init__(env)
        self.bot = Bot(env)

        for strategy_name in strategies:
            strategy_func = get_function_by_name("nle_code_wrapper.plugins.strategy.strategies", strategy_name)
            self.bot.strategy(strategy_func)
        self.action_space = gym.spaces.Discrete(len(self.bot.strategies))

    def reset(self, **kwargs):
        obs, info = self.bot.reset(**kwargs)

        return obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.bot.strategy_step(action)

        return obs, reward, terminated, truncated, info

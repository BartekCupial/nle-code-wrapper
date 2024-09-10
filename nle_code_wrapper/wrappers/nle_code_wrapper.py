from typing import Callable, List

import gymnasium as gym

from nle_code_wrapper.bot import Bot


class NLECodeWrapper(gym.Wrapper):
    def __init__(self, env, strategies: List[Callable]):
        super().__init__(env)
        self.bot = Bot(env)

        for strategy_func in strategies:
            self.bot.strategy(strategy_func)
        self.action_space = gym.spaces.Discrete(len(self.bot.strategies))

    def reset(self, **kwargs):
        obs, info = self.bot.reset(**kwargs)

        return obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.bot.strategy_step(action)

        return obs, reward, terminated, truncated, info

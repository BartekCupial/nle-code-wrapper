from typing import Callable, List

import gymnasium as gym
import numpy as np

from nle_code_wrapper.bot import Bot


class NLECodeWrapper(gym.Wrapper):
    def __init__(self, env, strategies: List[Callable]):
        super().__init__(env)
        self.bot = Bot(env)

        for strategy_func in strategies:
            self.bot.strategy(strategy_func)
        self.action_space = gym.spaces.Discrete(100)  # TODO: Change this to the number of actions in the action space
        self.observation_space = gym.spaces.Dict(
            {"strategy_steps": gym.spaces.Box(low=0, high=255, shape=(1,)), **self.env.observation_space}
        )

    def reset(self, **kwargs):
        obs, info = self.bot.reset(**kwargs)
        obs["strategy_steps"] = np.array([info["episode_extra_stats"]["strategy_steps"]])

        return obs, info

    def step(self, action):
        # allow for passing of action as string
        if isinstance(action, str):
            # preprocess action
            try:
                action = [s.__name__ for s in self.bot.strategies].index(action)
            except:
                # sample random index with high of len self.bot.strategies
                print("WARNING: Invalid action passed. Sampling random strategy.")
                action = np.random.randint(0, len(self.bot.strategies))

        obs, reward, terminated, truncated, info = self.bot.strategy_step(action)
        obs["strategy_steps"] = np.array([info["episode_extra_stats"]["strategy_steps"]])

        return obs, reward, terminated, truncated, info

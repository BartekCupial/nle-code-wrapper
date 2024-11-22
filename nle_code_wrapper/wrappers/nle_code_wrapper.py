from typing import Any, Callable, Dict, List, Tuple, Union

import gymnasium as gym
import numpy as np
from nle_utils.wrappers.gym_compatibility import GymV21CompatibilityV0
from numpy import int64, ndarray

from nle_code_wrapper.bot import Bot


class NLECodeWrapper(gym.Wrapper):
    def __init__(self, env: GymV21CompatibilityV0, strategies: List[Callable], max_strategy_steps: int = 100) -> None:
        super().__init__(env)
        self.bot = Bot(env, max_strategy_steps=max_strategy_steps)

        for strategy_func in strategies:
            self.bot.strategy(strategy_func)
        self.action_space = gym.spaces.Discrete(100)  # TODO: Change this to the number of actions in the action space
        self.observation_space = gym.spaces.Dict(
            {"strategy_steps": gym.spaces.Box(low=0, high=255, shape=(1,)), **self.env.observation_space}
        )

    def reset(self, **kwargs) -> Tuple[Dict[str, ndarray], Dict[str, Any]]:
        obs, info = self.bot.reset(**kwargs)
        obs["strategy_steps"] = np.array([info["episode_extra_stats"]["strategy_steps"]])

        return obs, info

    def step(self, action: Union[int64, int]) -> Tuple[Dict[str, ndarray], float, bool, bool, Dict[str, Any]]:
        obs, reward, terminated, truncated, info = self.bot.strategy_step(action)
        obs["strategy_steps"] = np.array([info["episode_extra_stats"]["strategy_steps"]])

        return obs, reward, terminated, truncated, info

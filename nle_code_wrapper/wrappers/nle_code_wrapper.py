from typing import Any, Callable, Dict, List, Tuple, Union

import gymnasium as gym
import numpy as np
from nle.nethack import actions as A
from numpy import int64, ndarray

from nle_code_wrapper.bot import Bot


class NLECodeWrapper(gym.Wrapper):
    def __init__(
        self,
        env: gym.Env,
        strategies: List[Callable],
        panics: List[Callable],
        max_strategy_steps: int = 1000,
        gamma: float = 0.99,
    ) -> None:
        super().__init__(env)
        if max_strategy_steps is None:
            max_strategy_steps = env.unwrapped._max_episode_steps
        self.bot = Bot(env, max_strategy_steps=max_strategy_steps, gamma=gamma)

        for panic_func in panics:
            self.bot.panic(panic_func)

        for strategy_func in strategies:
            self.bot.strategy(strategy_func)

        self.action_space = gym.spaces.Discrete(len(self.bot.strategies))
        self.observation_space = gym.spaces.Dict(
            {"env_steps": gym.spaces.Box(low=0, high=255, shape=(1,)), **self.env.observation_space}
        )

    def reset(self, **kwargs) -> Tuple[Dict[str, ndarray], Dict[str, Any]]:
        obs, info = self.bot.reset(**kwargs)
        obs["env_steps"] = np.array([info["episode_extra_stats"]["env_steps"]])

        return obs, info

    def step(self, action: Union[int64, int]) -> Tuple[Dict[str, ndarray], float, bool, bool, Dict[str, Any]]:
        obs, reward, terminated, truncated, info = self.bot.strategy_step(action)
        obs["env_steps"] = np.array([info["episode_extra_stats"]["env_steps"]])

        return obs, reward, terminated, truncated, info

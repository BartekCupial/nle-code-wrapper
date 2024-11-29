from functools import partial
from string import ascii_lowercase, ascii_uppercase
from typing import Any, Callable, Dict, List, Tuple, Union

import gymnasium as gym
import numpy as np
from nle.nethack.actions import CompassCardinalDirection, CompassIntercardinalDirection, MiscDirection
from nle_utils.wrappers.gym_compatibility import GymV21CompatibilityV0
from numpy import int64, ndarray

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def letter_strategy(bot: Bot, letter: str) -> bool:
    # only use the letter strategy if the bot is asking for a letter
    if bot.cursor[0] == [0]:
        bot.step(ord(letter))
        # Note:we don't want to count strategy steps when we are typing a letter
        bot.strategy_steps -= 1
        return True
    else:
        return False


@strategy
def direction_strategy(
    bot: "Bot", direction: Union[CompassCardinalDirection, CompassIntercardinalDirection, MiscDirection]
) -> bool:
    # only use the direction strategy if the bot is asking for a direction
    if "In what direction?" in bot.message:
        bot.step(direction)
        # Note:we don't want to count strategy steps when we are typing a letter
        bot.strategy_steps -= 1
        return True
    else:
        return False


class NLECodeWrapper(gym.Wrapper):
    def __init__(
        self, env: GymV21CompatibilityV0, strategies: List[Callable], max_strategy_steps: int = 100, gamma: float = 0.99
    ) -> None:
        super().__init__(env)
        self.bot = Bot(env, max_strategy_steps=max_strategy_steps)

        for strategy_func in strategies:
            self.bot.strategy(strategy_func)

        # add letter strategies to action space
        for char in ascii_lowercase + ascii_uppercase:
            strategy_func = partial(letter_strategy, letter=char)
            strategy_func.__name__ = char
            self.bot.strategy(strategy_func)

        directions = {
            "north": CompassCardinalDirection.N,
            "south": CompassCardinalDirection.S,
            "east": CompassCardinalDirection.E,
            "west": CompassCardinalDirection.W,
            "north_east": CompassIntercardinalDirection.NE,
            "north_west": CompassIntercardinalDirection.NW,
            "south_east": CompassIntercardinalDirection.SE,
            "south_west": CompassIntercardinalDirection.SW,
            "up": MiscDirection.UP,
            "down": MiscDirection.DOWN,
            "wait": MiscDirection.WAIT,
        }

        # add direction strategies to action space
        for direction, action in directions.items():
            strategy_func = partial(direction_strategy, direction=action)
            strategy_func.__name__ = direction
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

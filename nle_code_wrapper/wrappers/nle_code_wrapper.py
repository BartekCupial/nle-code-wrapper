from functools import partial
from string import ascii_lowercase, ascii_uppercase
from typing import Any, Callable, Dict, List, Tuple, Union

import gymnasium as gym
import numpy as np
from nle.nethack import actions as A
from nle_utils.wrappers.gym_compatibility import GymV21CompatibilityV0
from numpy import int64, ndarray

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def more(bot: Bot) -> bool:
    bot.step(A.MiscAction.MORE)
    bot.strategy_steps -= 1
    return True


@strategy
def letter_strategy(bot: Bot, letter: str) -> bool:
    # allow typing letters because:
    #   1) `in_yn_function` for yes/no answer
    #   2) `in_getlin`, for typing in topline, example engraving
    #   3) `xwaitingforspace` for typing a letter when we are asked about the item pile "Pick up what?" or when looting a chest
    if bot.in_yn_function or bot.in_getlin or bot.xwaitingforspace:
        bot.step(ord(letter))
        bot.strategy_steps -= 1
        return True
    else:
        return False


@strategy
def direction_strategy(
    bot: "Bot", direction: Union[A.CompassCardinalDirection, A.CompassIntercardinalDirection, A.MiscDirection]
) -> bool:
    if "In what direction?" in bot.message:
        # Note:we don't want to count strategy steps when we are typing a letter
        bot.strategy_steps -= 1

    bot.step(direction)
    return True


class NLECodeWrapper(gym.Wrapper):
    def __init__(
        self,
        env: GymV21CompatibilityV0,
        strategies: List[Callable],
        panics: List[Callable],
        max_strategy_steps: int = 1000,
        add_letter_strategies: bool = True,
        add_direction_strategies: bool = True,
        add_more_strategy: bool = True,
        gamma: float = 0.99,
    ) -> None:
        super().__init__(env)
        if max_strategy_steps is None:
            max_strategy_steps = env.gym_env.unwrapped._max_episode_steps
        self.bot = Bot(env, max_strategy_steps=max_strategy_steps, gamma=gamma)

        for panic_func in panics:
            self.bot.panic(panic_func)

        for strategy_func in strategies:
            self.bot.strategy(strategy_func)

        if add_letter_strategies:
            # add letter strategies to action space
            for char in ascii_lowercase + ascii_uppercase:
                strategy_func = partial(letter_strategy, letter=char)
                strategy_func.__name__ = char
                strategy_func.__doc__ = ""
                self.bot.strategy(strategy_func)

        directions = {
            "north": A.CompassCardinalDirection.N,
            "south": A.CompassCardinalDirection.S,
            "east": A.CompassCardinalDirection.E,
            "west": A.CompassCardinalDirection.W,
            "north_east": A.CompassIntercardinalDirection.NE,
            "north_west": A.CompassIntercardinalDirection.NW,
            "south_east": A.CompassIntercardinalDirection.SE,
            "south_west": A.CompassIntercardinalDirection.SW,
            "up": A.MiscDirection.UP,
            "down": A.MiscDirection.DOWN,
            "wait": A.MiscDirection.WAIT,
        }

        if add_direction_strategies:
            # add direction strategies to action space
            for direction, action in directions.items():
                strategy_func = partial(direction_strategy, direction=action)
                strategy_func.__name__ = direction
                strategy_func.__doc__ = ""
                self.bot.strategy(strategy_func)

        if add_more_strategy:
            # add more strategy
            self.bot.strategy(more)

        def noop(bot):
            """
            Wastes move
            """
            return

        self.bot.strategy(noop)

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

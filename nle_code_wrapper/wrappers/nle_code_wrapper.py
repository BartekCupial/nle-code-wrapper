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
    if bot.cursor[0] == [0]:
        # Note:we don't want to count strategy steps when we are typing a letter
        bot.strategy_steps -= 1
    # TODO: for now allow typing letters because:
    #       1) inventory cannot be shown when we allow letters only on first row
    #       2) sometimes we need to type a letter when we are asked about the item pile "Pick up what?"
    #       3) sometimes we need to type a letter when looting a chest
    bot.step(ord(letter))
    return True


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
        max_strategy_steps: int = 100,
        gamma: float = 0.99,
        add_letter_strategies: bool = True,
        add_direction_strategies: bool = True,
        add_more_strategy: bool = True,
    ) -> None:
        super().__init__(env)
        self.bot = Bot(env, max_strategy_steps=max_strategy_steps)

        for panic_func in panics:
            self.bot.panic(panic_func)

        for strategy_func in strategies:
            self.bot.strategy(strategy_func)

        # add letter strategies to action space
        if add_letter_strategies:
            for char in ascii_lowercase + ascii_uppercase:
                strategy_func = partial(letter_strategy, letter=char)
                strategy_func.__name__ = char
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

        # add direction strategies to action space
        if add_direction_strategies:
            for direction, action in directions.items():
                strategy_func = partial(direction_strategy, direction=action)
                strategy_func.__name__ = direction
                self.bot.strategy(strategy_func)

        # add more strategy
        if add_more_strategy:
            self.bot.strategy(more)

        self.action_space = gym.spaces.Discrete(len(self.bot.strategies))
        self.observation_space = gym.spaces.Dict(
            {"env_steps": gym.spaces.Box(low=0, high=255, shape=(1,)), **self.env.observation_space}
        )

    def reset(self, **kwargs) -> Tuple[Dict[str, ndarray], Dict[str, Any]]:
        obs, info = self.bot.reset(**kwargs)
        obs["env_steps"] = np.array([info["episode_extra_stats"]["env_steps"]])

        return obs, info

    def step(self, action: Union[int64, int]) -> Tuple[Dict[str, ndarray], float, bool, bool, Dict[str, Any]]:
        if isinstance(action, str):
            try:
                # preprocess action
                action = action.lower()
                if "strategy:" in action.lower():
                    action = action.split("strategy:")[1].strip()

                action = [s.__name__ for s in self.bot.strategies].index(action)
            except:
                print("WARNING: Unparsable action passed. Setting action = len(self.bot.strategies)")
                action = len(self.bot.strategies)  # set to invalid action

        obs, reward, terminated, truncated, info = self.bot.strategy_step(action)
        obs["env_steps"] = np.array([info["episode_extra_stats"]["env_steps"]])

        return obs, reward, terminated, truncated, info

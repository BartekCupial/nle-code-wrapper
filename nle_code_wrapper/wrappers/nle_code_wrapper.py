import os
import pickle
import time
from functools import partial
from pathlib import Path
from string import ascii_lowercase, ascii_uppercase
from typing import Any, Callable, Dict, List, Tuple, Union

import gymnasium as gym
import numpy as np
from nle import nethack
from nle.nethack import actions as A
from nle_utils.utils.utils import log
from nle_utils.wrappers.gym_compatibility import GymV21CompatibilityV0
from numpy import int64, ndarray

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy
from nle_code_wrapper.utils.seed import get_unique_seed


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
        failed_game_path: str = None,
    ) -> None:
        super().__init__(env)
        self.failed_game_path = failed_game_path
        self.episode_number = 0

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

    def reset(self, seed=None, **kwargs) -> Tuple[Dict[str, ndarray], Dict[str, Any]]:
        if seed is None:
            seed = get_unique_seed(episode_idx=self.episode_number)

        self.recorded_seed = seed
        self.recorded_actions = []
        self.named_actions = []
        self.episode_number += 1

        try:
            obs, info = self.bot.reset(seed=seed, **kwargs)
            obs["env_steps"] = np.array([info["episode_extra_stats"]["env_steps"]])
        except Exception as e:
            self.save_to_file()
            raise e

        return obs, info

    def step(self, action: Union[int64, int]) -> Tuple[Dict[str, ndarray], float, bool, bool, Dict[str, Any]]:
        try:
            self.recorded_actions.append(action)
            self.named_actions.append(self.bot.strategies[action].__name__)

            obs, reward, terminated, truncated, info = self.bot.strategy_step(action)
            obs["env_steps"] = np.array([info["episode_extra_stats"]["env_steps"]])
        except Exception as e:
            self.save_to_file()
            log.error(f"Bot failed due to unhandled exception: {e}")
            self.bot.current_obs["env_steps"] = np.array([0])
            return self.bot.current_obs, 0, True, False, {}

        return obs, reward, terminated, truncated, info

    def save_to_file(self):
        dat = {
            "actions": self.recorded_actions,
            "seed": self.recorded_seed,
        }
        og_ttyrec = self.env.unwrapped.nethack._ttyrec
        if og_ttyrec is not None:
            ttyrec = Path(og_ttyrec).stem
        else:
            ttyrec_prefix = f"nle.{os.getpid()}.{self.recorded_seed}"
            ttyrec_version = f".ttyrec{nethack.TTYREC_VERSION}.bz2"
            ttyrec = ttyrec_prefix + ttyrec_version

        fname = os.path.join(self.failed_game_path, f"{ttyrec}.demo")
        with open(fname, "wb") as f:
            log.debug(f"Saving demo to {fname}...")
            pickle.dump(dat, f)

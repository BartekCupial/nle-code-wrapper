import inspect
import itertools
from argparse import Namespace
from functools import partial
from typing import Any, Callable, Dict, List, Tuple, Union

from nle.nethack import actions as A
from nle.nethack.actions import Command, CompassDirection
from nle_utils.blstats import BLStats
from nle_utils.wrappers.gym_compatibility import GymV21CompatibilityV0
from numpy import int64, ndarray, uint8

from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.exceptions import BotFinished, BotPanic
from nle_code_wrapper.bot.level import Level
from nle_code_wrapper.bot.pathfinder import Pathfinder
from nle_code_wrapper.bot.pvp import Pvp
from nle_code_wrapper.utils.inspect import check_strategy_parameters


class Bot:
    def __init__(
        self, env: Union[GymV21CompatibilityV0, Namespace], max_strategy_steps: int = 100, gamma: float = 0.99
    ) -> None:
        """
        Gym environment or Namespace with the same attributes as the gym environment
        """

        self.env = env
        self.gamma = gamma
        self.pathfinder: Pathfinder = Pathfinder(self)
        self.pvp: Pvp = Pvp(self)
        self.strategies: list[Callable] = []
        self.max_strategy_steps = max_strategy_steps

    def strategy(self, func: Union[partial, Callable]) -> None:
        """
        Decorator to add a strategy to the bot

        Args:
            func: function to add as a strategy
        """
        self.strategies.append(func)

    @property
    def blstats(self) -> BLStats:
        return BLStats(*self.last_obs["blstats"])

    @property
    def glyphs(self) -> ndarray:
        """

        Returns:
            2D numpy array with the glyphs
        """
        return self.last_obs["glyphs"]

    @property
    def message(self) -> str:
        """
        Returns:
            str with the message
        """
        return bytes(self.last_obs["message"]).decode("latin-1").rstrip("\x00")

    @property
    def inv_glyphs(self) -> ndarray:
        return self.last_obs["inv_glyphs"]

    @property
    def inv_letters(self) -> ndarray:
        return self.last_obs["inv_letters"]

    @property
    def inv_oclasses(self) -> ndarray:
        return self.last_obs["inv_oclasses"]

    @property
    def cursor(self):
        return tuple(self.last_obs["tty_cursor"])

    @property
    def entity(self) -> Entity:
        """
        Returns:
            Entity object with the player
        """
        position = (self.blstats.y, self.blstats.x)
        return Entity(position, self.glyphs[position])

    @property
    def entities(self) -> List[Union[Any, Entity]]:
        """
        Returns:
            List of Entity objects with the monsters
        """
        return [Entity(position, self.glyphs[position]) for position in zip(*self.pvp.get_monster_mask().nonzero())]

    def reset(self, **kwargs) -> Tuple[Dict[str, ndarray], Dict[str, Dict[str, Any]]]:
        """
        Reset the environment and the bot. It also updates the last_obs and last_info.

        Args:
            **kwargs -parameters to reset the environment
        Returns:
            observation and info
        """

        self.levels = {}
        self.steps = 0
        self.reward = 0.0
        self.current_strategy = None
        self.current_args = None
        self.strategy_steps = 0

        self.last_obs, self.last_info = self.env.reset(**kwargs)

        extra_stats = self.last_info.get("episode_extra_stats", {})
        new_extra_stats = {
            "env_steps": self.steps,
            "strategy_reward": self.reward,
            "strategy_usefull": self.steps > 0,
        }
        self.last_info["episode_extra_stats"] = {**extra_stats, **new_extra_stats}

        self.update()

        return self.last_obs, self.last_info

    def step(self, action: int) -> None:
        """
        Take a step in the environment

        Args:
            action: action to take
        """
        self.last_obs, reward, self.terminated, self.truncated, self.last_info = self.env.step(
            self.env.actions.index(action)
        )

        self.steps += 1
        self.reward += reward * self.current_discount
        self.current_discount *= self.gamma

        if self.terminated or self.truncated:
            raise BotFinished

        self.update()

    def strategy_step(self, action: Union[int, int64]) -> Tuple[Dict[str, ndarray], float, bool, bool, Dict[str, Any]]:
        """
        Take a step in the environment using the strategies defined in the bot. If no strategy is chosen, the action
        will decide the strategy to use. If a strategy is chosen, the action will be passed as an argument to the strategy.

        Args:
            action: action to take
        Returns:
            observation, reward, done, info
        """
        self.steps = 0
        self.reward = 0
        self.current_discount = 1.0
        self.terminated = False
        self.truncated = False
        self.last_info = {}

        try:
            if self.current_strategy is None:
                if action < len(self.strategies):
                    self.current_strategy = self.strategies[action]
                    self.current_args = ()
                else:
                    # if action is wrong do nothing, we still should increment strategy_step
                    # this is only relevant for multiple arguments strategies
                    self.strategy_steps += 1
            else:
                self.current_args += (action,)

            # we need this if the strategy was not created because out of bounds
            if self.current_strategy is not None:
                # TODO: support in the future, keep in mind action space will have to be changed
                assert check_strategy_parameters(self.current_strategy) == 1, "For now ban on strategies with arguments"

                # If the strategy has all the arguments it needs, call it
                if check_strategy_parameters(self.current_strategy) == len(self.current_args) + 1:  # +1 for self
                    self.current_strategy(self, *self.current_args)
                    self.current_strategy = None
                    self.current_args = None
        except (BotPanic, BotFinished):
            self.current_strategy = None
            self.current_args = None

        extra_stats = self.last_info.get("episode_extra_stats", {})
        new_extra_stats = {
            "env_steps": self.steps,
            "strategy_reward": self.reward,
            "strategy_usefull": self.steps > 0,
        }

        if self.terminated or self.truncated:
            new_extra_stats["success_rate"] = self.last_info["end_status"].name == "TASK_SUCCESSFUL"
            new_extra_stats["strategy_steps"] = self.strategy_steps

        self.last_info["episode_extra_stats"] = {**extra_stats, **new_extra_stats}

        return self.last_obs, self.reward, self.terminated, self.truncated, self.last_info

    def search(self) -> None:
        self.step(A.Command.SEARCH)

        blstats = self.blstats
        x, y = blstats.x, blstats.y
        for i, j in itertools.product([-1, 0, 1], repeat=2):
            self.current_level.search_count[y + i, x + j] += 1

    def type_text(self, text: str) -> None:
        for char in text:
            self.step(ord(char))

    def update(self) -> None:
        self.current_level.update(self.glyphs, self.blstats)

    @property
    def current_level(self) -> Level:
        """
        :return: Level object of the current level
        """
        key = (self.blstats.dungeon_number, self.blstats.level_number)
        if key not in self.levels:
            self.levels[key] = Level(*key)
        return self.levels[key]

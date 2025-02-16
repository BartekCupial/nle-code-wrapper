import copy
import itertools
import re
from argparse import Namespace
from functools import partial
from typing import Any, Callable, Dict, List, Tuple, Union

import numpy as np
from nle import nethack
from nle.env.base import NLE
from nle.nethack import actions as A
from nle_utils.blstats import BLStats
from nle_utils.glyph import G
from nle_utils.wrappers.gym_compatibility import GymV21CompatibilityV0
from numpy import int64, ndarray

from nle_code_wrapper.bot.character import Character
from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.exceptions import BotFinished, BotPanic
from nle_code_wrapper.bot.inventory import InventoryManager
from nle_code_wrapper.bot.level import Level
from nle_code_wrapper.bot.pathfinder import Movements, Pathfinder
from nle_code_wrapper.bot.pvp import Pvp
from nle_code_wrapper.bot.trap_tracker import TrapTracker
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.inspect import check_strategy_parameters


class Bot:
    def __init__(
        self, env: Union[GymV21CompatibilityV0, Namespace], max_strategy_steps: int = 1000, gamma: float = 0.99
    ) -> None:
        """
        Gym environment or Namespace with the same attributes as the gym environment
        """

        self.env = env
        self.gamma = gamma

        self.movements: Movements = Movements(self)
        self.character: Character = Character(self, self.env.gym_env.unwrapped.character)
        self.pathfinder: Pathfinder = Pathfinder(self)
        self.inventory_mangager: InventoryManager = InventoryManager(self)
        self.pvp: Pvp = Pvp(self)
        self.trap_tracker: TrapTracker = TrapTracker(self)

        self.strategies: list[Callable] = []
        self.panics: list[Callable] = []
        self.max_strategy_steps = max_strategy_steps

    def strategy(self, func: Callable) -> None:
        """
        Decorator to add a strategy to the bot

        Args:
            func: function to add as a strategy
        """
        self.strategies.append(func)

    def panic(self, func: Callable) -> None:
        """
        Decorator to add a panic to the bot

        Args:
            func: function to add as a panic
        """
        self.panics.append(func)

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
        self.current_discount = 1.0

        self.current_obs, self.current_info = self.env.reset(**kwargs)
        self.last_obs = self.current_obs
        self.last_info = self.current_info

        extra_stats = self.current_info.get("episode_extra_stats", {})
        new_extra_stats = {
            "env_steps": self.steps,
            "strategy_reward": self.reward,
            "strategy_usefull": self.steps > 0,
        }
        self.current_info["episode_extra_stats"] = {**extra_stats, **new_extra_stats}

        self.update()
        self.start_glyph = self.entity.glyph

        return self.current_obs, self.current_info

    def step(self, action: int) -> None:
        """
        Take a step in the environment

        Args:
            action: action to take
        """
        self.last_obs = copy.deepcopy(self.current_obs)
        self.last_info = copy.deepcopy(self.current_info)
        try:
            self.current_obs, reward, self.terminated, self.truncated, self.current_info = self.env.step(
                self.env.actions.index(action)
            )
        except ValueError as e:
            # Handle the case where the action is not in the list of allowed actions,
            # many minihack environments only allow subset of possible actions
            if str(e) == "tuple.index(x): x not in tuple":
                raise BotPanic(f"action not allowed, err: {e}")
            else:
                raise e

        self.steps += 1
        self.reward += reward * self.current_discount
        self.current_discount *= self.gamma

        if self.terminated or self.truncated:
            raise BotFinished

        self.update()
        self.check_panics()

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
        self.current_info = {}

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
                assert (
                    check_strategy_parameters(self.current_strategy) == 1
                ), f"For now ban on strategies with arguments, {self.current_strategy.__name__}"

                # If the strategy has all the arguments it needs, call it
                if check_strategy_parameters(self.current_strategy) == len(self.current_args) + 1:  # +1 for self
                    self.current_strategy(self, *self.current_args)
                    self.current_strategy = None
                    self.current_args = None
        except (BotPanic, BotFinished):
            self.current_strategy = None
            self.current_args = None

        extra_stats = self.current_info.get("episode_extra_stats", {})
        new_extra_stats = {
            "env_steps": self.steps,
            "strategy_reward": self.reward,
            "strategy_usefull": self.steps > 0,
        }

        if "end_status" not in self.current_info:
            # this will happen when we exceed max_strategy_steps
            self.current_info["end_status"] = NLE.StepStatus.ABORTED

        if self.terminated or self.truncated:
            new_extra_stats["success_rate"] = self.current_info["end_status"].name == "TASK_SUCCESSFUL"
            new_extra_stats["strategy_steps"] = self.strategy_steps

        self.current_info["episode_extra_stats"] = {**extra_stats, **new_extra_stats}

        return self.current_obs, self.reward, self.terminated, self.truncated, self.current_info

    def search(self, num_times=1) -> None:
        old_time = self.blstats.time
        for char in str(num_times):
            self.type_text(char)
        self.step(A.Command.SEARCH)
        turn_diff = self.blstats.time - old_time

        blstats = self.blstats
        x, y = blstats.x, blstats.y
        height, width = self.glyphs.shape
        for i, j in itertools.product([-1, 0, 1], repeat=2):
            # make sure we don't have out of bounds
            if not (0 <= y + i < height) or not (0 <= x + j < width):
                continue

            self.current_level.search_count[y + i, x + j] += turn_diff

    def wait(self) -> None:
        if A.Command.SEARCH in self.env.actions:
            self.search()
        elif A.MiscDirection.WAIT in self.env.actions:
            self.step(A.MiscDirection.WAIT)
        else:
            self.pathfinder.random_move()

    def type_text(self, text: str) -> None:
        for char in text:
            self.step(ord(char))

    def check_panics(self):
        for panic in self.panics:
            panic(self)

    def update(self) -> None:
        internal = self.env.gym_env.unwrapped.last_observation[self.env.gym_env.unwrapped._internal_index]
        self.in_yn_function = internal[1]
        self.in_getlin = internal[2]
        self.xwaitingforspace = internal[3]

        self.blstats = self.get_blstats(self.current_obs)
        self.glyphs = self.get_glyphs(self.current_obs)
        self.message = self.get_message(self.current_obs)
        self.tty_chars = self.get_tty_chars(self.current_obs)
        self.tty_colors = self.get_tty_colors(self.current_obs)
        self.cursor = self.get_cursor(self.current_obs)
        self.entity = self.get_entity(self.current_obs)
        self.entities = self.get_entities(self.current_obs)
        self.current_level = self.get_current_level(self.current_obs)

        self.current_level.update(self.glyphs, self.blstats)
        self.inventory_mangager.update()
        self.character.update()
        self.movements.update()
        self.pathfinder.update()
        self.pvp.update()
        self.trap_tracker.update()

    def get_blstats(self, last_obs) -> BLStats:
        return BLStats(*last_obs["blstats"])

    def get_glyphs(self, last_obs) -> ndarray:
        """

        Returns:
            2D numpy array with the glyphs
        """
        return last_obs["glyphs"]

    def get_message(self, last_obs) -> str:
        """
        Returns:
            str with the message
        """
        return last_obs["text_message"]

    def get_tty_chars(self, last_obs):
        return last_obs["tty_chars"]

    def get_tty_colors(self, last_obs):
        return last_obs["tty_colors"]

    def get_cursor(self, last_obs):
        return tuple(last_obs["tty_cursor"])

    def get_entity(self, last_obs) -> Entity:
        """
        Returns:
            Entity object with the player
        """
        blstats = self.get_blstats(last_obs)
        position = (blstats.y, blstats.x)
        return Entity(position, self.get_glyphs(last_obs)[position])

    def get_entities(self, last_obs) -> List[Union[Any, Entity]]:
        """
        Returns:
            List of Entity objects with the monsters
        """
        glyphs = self.get_glyphs(last_obs)
        blstats = self.get_blstats(last_obs)
        monster_mask = utils.isin(glyphs, G.MONS, G.INVISIBLE_MON)
        monster_mask[blstats.y, blstats.x] = 0

        return [Entity(position, glyphs[position]) for position in list(zip(*np.where(monster_mask)))]

    def get_current_level(self, last_obs) -> Level:
        """
        :return: Level object of the current level
        """
        blstats = self.get_blstats(last_obs)
        key = (blstats.dungeon_number, blstats.level_number)
        if key not in self.levels:
            self.levels[key] = Level(*key)
        return self.levels[key]

    @property
    def inventory(self):
        return self.inventory_mangager.inventory

    @property
    def engulfed(self):
        return utils.isin(self.glyphs, G.SWALLOW).any()

    @property
    def stone(self):
        """Stoned"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_STONE else False

    @property
    def slime(self):
        """Slimed"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_SLIME else False

    @property
    def strngl(self):
        """Strangled"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_STRNGL else False

    @property
    def foodpois(self):
        """Food Poisoning"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_FOODPOIS else False

    @property
    def termill(self):
        """Terminally Ill"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_TERMILL else False

    @property
    def blind(self):
        """Blind"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_BLIND else False

    @property
    def deaf(self):
        """Deaf"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_DEAF else False

    @property
    def stun(self):
        """Stunned"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_STUN else False

    @property
    def conf(self):
        """Confused"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_CONF else False

    @property
    def hallu(self):
        """Hallucinating"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_HALLU else False

    @property
    def lev(self):
        """Levitating"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_LEV else False

    @property
    def fly(self):
        """Flying"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_FLY else False

    @property
    def ride(self):
        """Riding"""
        return True if self.blstats.prop_mask & nethack.BL_MASK_RIDE else False

    @property
    def poly(self):
        """Polymorphed"""
        return self.start_glyph != self.entity.glyph

    @property
    def trap(self) -> bool:
        """Trapped"""
        return self.trap_tracker.trapped

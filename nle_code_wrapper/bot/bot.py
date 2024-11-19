import inspect
from functools import partial
from typing import Callable

from nle.nethack import actions as A
from nle_utils.blstats import BLStats

from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.exceptions import BotFinished, BotPanic
from nle_code_wrapper.bot.level import Level
from nle_code_wrapper.bot.pathfinder import Pathfinder
from nle_code_wrapper.bot.pvp import Pvp
from nle_code_wrapper.utils.inspect import check_strategy_parameters


class Bot:
    def __init__(self, env, gamma: float = 0.99):
        self.env = env
        self.gamma = gamma
        self.pathfinder: Pathfinder = Pathfinder(self)
        self.pvp: Pvp = Pvp(self)
        self.strategies: list[Callable] = []

    def strategy(self, func):
        self.strategies.append(func)

    @property
    def blstats(self):
        return BLStats(*self.last_obs["blstats"])

    @property
    def glyphs(self):
        return self.last_obs["glyphs"]

    @property
    def message(self):
        return bytes(self.last_obs["message"]).decode("latin-1").rstrip("\x00")

    @property
    def inv_glyphs(self):
        return self.last_obs["inv_glyphs"]

    @property
    def inv_letters(self):
        return self.last_obs["inv_letters"]

    @property
    def inv_oclasses(self):
        return self.last_obs["inv_oclasses"]

    @property
    def cursor(self):
        return tuple(self.last_obs["tty_cursor"])

    @property
    def entity(self):
        position = (self.blstats.y, self.blstats.x)
        return Entity(position, self.glyphs[position])

    @property
    def entities(self):
        return [Entity(position, self.glyphs[position]) for position in zip(*self.pvp.get_monster_mask().nonzero())]

    def reset(self, **kwargs):
        self.levels = {}
        self.steps = 0
        self.reward = 0.0
        self.current_strategy = None
        self.current_args = None

        self.done = False

        self.last_obs, self.last_info = self.env.reset(**kwargs)

        extra_stats = self.last_info.get("episode_extra_stats", {})
        new_extra_stats = {
            "strategy_steps": self.steps,
            "strategy_reward": self.reward,
            "strategy_usefull": self.steps > 0,
        }
        self.last_info["episode_extra_stats"] = {**extra_stats, **new_extra_stats}

        self.update()

        return self.last_obs, self.last_info

    def step(self, action):
        self.last_obs, reward, self.terminated, self.truncated, self.last_info = self.env.step(
            self.env.actions.index(action)
        )

        self.steps += 1
        self.reward += reward * self.current_discount
        self.current_discount *= self.gamma

        if self.terminated or self.truncated:
            self.done = True
            raise BotFinished

        self.update()

    def strategy_step(self, action):
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
                # if action is wrong do nothing
                # TODO: we need to write tests so they sample from correct action space
            else:
                self.current_args += (action,)

            # we need this if the strategy was not created because out of bounds
            if self.current_strategy is not None:
                # If the strategy has all the arguments it needs, call it
                if check_strategy_parameters(self.current_strategy) == len(self.current_args) + 1:  # +1 for self
                    self.current_strategy(self, *self.current_args)
                    self.current_strategy = None
                    self.current_args = None
        except (BotPanic, BotFinished):
            pass

        extra_stats = self.last_info.get("episode_extra_stats", {})
        new_extra_stats = {
            "strategy_steps": self.steps,
            "strategy_reward": self.reward,
            "strategy_usefull": self.steps > 0,
        }

        if self.terminated or self.truncated:
            new_extra_stats["success_rate"] = self.last_info["end_status"].name == "TASK_SUCCESSFUL"

        self.last_info["episode_extra_stats"] = {**extra_stats, **new_extra_stats}

        return self.last_obs, self.reward, self.terminated, self.truncated, self.last_info

    def search(self):
        self.step(A.Command.SEARCH)
        self.current_level().search_count[self.blstats.y, self.blstats.x] += 1

    def type_text(self, text):
        for char in text:
            self.step(ord(char))

    def update(self):
        self.current_level().update(self.glyphs, self.blstats)

    def current_level(self) -> Level:
        key = (self.blstats.dungeon_number, self.blstats.level_number)
        if key not in self.levels:
            self.levels[key] = Level(*key)
        return self.levels[key]

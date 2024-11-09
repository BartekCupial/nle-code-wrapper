from nle.nethack import actions as A
from nle_utils.blstats import BLStats

from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.exceptions import BotFinished, BotPanic
from nle_code_wrapper.bot.level import Level
from nle_code_wrapper.bot.pathfinder import Pathfinder
from nle_code_wrapper.bot.pvp import Pvp
from nle_code_wrapper.bot.strategy import Panic, Strategy


class Bot:
    def __init__(self, env):
        self.env = env
        self.pathfinder: Pathfinder = Pathfinder(self)
        self.pvp: Pvp = Pvp(self)
        self.strategies: list[Strategy] = []
        self.panics: list[Panic] = []

    def strategy(self, func):
        self.strategies.append(func(self))

    def panic(self, func):
        self.panics.append(func(self))

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
        for strategy in self.strategies:
            strategy.reset()
        for panic in self.panics:
            panic.reset()

        self.levels = {}
        self.steps = 0
        self.reward = 0.0

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
        self.reward += reward

        if self.terminated or self.truncated:
            self.done = True
            raise BotFinished

        self.update()
        self.check_panics()

    def strategy_step(self, action):
        self.steps = 0
        self.reward = 0
        self.terminated = False
        self.truncated = False
        self.last_info = {}

        strategy = self.strategies[action]
        try:
            strategy()
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

    def check_panics(self):
        for panic in self.panics:
            panic()

    def current_level(self) -> Level:
        key = (self.blstats.dungeon_number, self.blstats.level_number)
        if key not in self.levels:
            self.levels[key] = Level(*key)
        return self.levels[key]

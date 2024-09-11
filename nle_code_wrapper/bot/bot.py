from nle.nethack import actions as A
from nle_utils.blstats import BLStats

from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.exceptions import BotFinished, BotPanic
from nle_code_wrapper.bot.level import Level
from nle_code_wrapper.plugins.pathfinder import Pathfinder
from nle_code_wrapper.plugins.pvp import Pvp


class Bot:
    def __init__(self, env):
        self.env = env
        self.pathfinder: Pathfinder = Pathfinder(self)
        self.pvp: Pvp = Pvp(self)
        self.strategies = []
        self.panics = []

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
    def cursor(self):
        return tuple(self.last_obs["tty_cursor"])

    @property
    def entity(self):
        position = (self.blstats.y, self.blstats.x)
        return Entity(position, self.glyphs[position])

    @property
    def entities(self):
        return [
            Entity(position, self.glyphs[position])
            for position in zip(*self.pvp.monster_tracker.get_monster_mask().nonzero())
        ]

    def reset(self, **kwargs):
        self.levels = {}
        self.steps = 0
        self.reward = 0.0

        self.done = False

        self.last_obs, self.last_info = self.env.reset(**kwargs)
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
        self.terminated = 0
        self.truncated = 0
        self.last_info = {}

        strategy = self.strategies[action]
        try:
            strategy()
        except (BotPanic, BotFinished):
            pass

        self.last_info["steps"] = self.steps

        return self.last_obs, self.reward, self.terminated, self.truncated, self.last_info

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

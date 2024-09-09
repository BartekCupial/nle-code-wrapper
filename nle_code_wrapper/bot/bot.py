from nle.nethack import actions as A
from nle_utils.blstats import BLStats
from nle_utils.glyph import G

from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.exceptions import BotFinished
from nle_code_wrapper.bot.level import Level
from nle_code_wrapper.envs.create_env import create_env
from nle_code_wrapper.plugins.pathfinder import Pathfinder
from nle_code_wrapper.plugins.pvp import Pvp
from nle_code_wrapper.plugins.strategy import StrategyManager
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.attr_dict import AttrDict


class Bot:
    def __init__(self, cfg):
        self.cfg = cfg
        self.pathfinder: Pathfinder = Pathfinder(self)
        self.pvp: Pvp = Pvp(self)
        self.strategy_manager: StrategyManager = StrategyManager(self)

    def strategy(self, func):
        return self.strategy_manager.strategy(func)

    def panic(self, func):
        return self.strategy_manager.panic(func)

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
    def position(self):
        return self.blstats.y, self.blstats.x

    @property
    def entity(self):
        return Entity(self.position, self.glyphs[self.position])

    @property
    def entities(self):
        return [
            Entity(position, self.glyphs[position])
            for position in zip(*self.pvp.monster_tracker.get_monster_mask().nonzero())
        ]

    def global_strategy(self):
        return self.strategy_manager.run_strategies()

    def main(self):
        render_mode = "human"
        if self.cfg.no_render:
            render_mode = None

        self.env = create_env(
            self.cfg.env,
            cfg=self.cfg,
            env_config=AttrDict(worker_index=0, vector_index=0, env_id=0),
            render_mode=render_mode,
        )

        self.levels = {}
        self.steps = 0
        self.reward = 0.0

        self.done = False
        self.last_obs, self.last_info = self.env.reset(seed=self.cfg.seed)

        self.update()

        try:
            for _ in self.global_strategy():
                pass
        except BotFinished:
            pass

        if render_mode is not None:
            print(
                f"Bot finished, episode done: {self.done}, episode reward: {self.reward}, episode steps: {self.steps}"
            )

        return self.last_info["end_status"]

    def step(self, action):
        self.last_obs, reward, terminated, truncated, self.last_info = self.env.step(self.env.actions.index(action))

        self.steps += 1
        self.reward += reward

        if terminated or truncated:
            self.done = True
            raise BotFinished

        self.update()
        self.strategy_manager.check_panics()

    def type_text(self, text):
        for char in text:
            self.step(ord(char))

    def kick(self, dir):
        self.step(A.Command.KICK)
        self.direction(dir)

    def pray(self):
        self.step(A.Command.PRAY)

    def quaff(self):
        self.step(A.Command.QUAFF)

    def read(self):
        self.step(A.Command.READ)

    def puton(self):
        self.step(A.Command.PUTON)

    def wear(self):
        self.step(A.Command.WEAR)

    def wield(self):
        self.step(A.Command.WIELD)

    def zap(self):
        self.step(A.Command.ZAP)

    def inventory(self):
        self.step(A.Command.INVENTORY)

    def look(self):
        self.step(A.Command.LOOK)

    def pickup(self):
        self.step(A.Command.PICKUP)

    def apply(self):
        self.step(A.Command.APPLY)
        # TODO: handle multiple items
        # self.type_text(self.inventory.items.get_letter(item))

    def eat(self):
        self.step(A.Command.EAT)

    def direction(self, dir):
        self.pathfinder.direction(dir)

    def update(self):
        self.current_level().update(self.glyphs, self.blstats)

    def current_level(self) -> Level:
        key = (self.blstats.dungeon_number, self.blstats.level_number)
        if key not in self.levels:
            self.levels[key] = Level(*key)
        return self.levels[key]

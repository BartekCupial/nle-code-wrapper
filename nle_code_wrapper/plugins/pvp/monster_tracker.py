import numpy as np
from nle_utils.glyph import C, G

from nle_code_wrapper.utils import utils


class MonsterTracker:
    def __init__(self, bot):
        self.bot = bot
        # self.peaceful_monster_mask = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        # self.monster_mask = np.zeros((C.SIZE_Y, C.SIZE_X), bool)

    def get_monster_mask(self):
        monster_mask = utils.isin(self.bot.glyphs, G.MONS, G.INVISIBLE_MON)
        monster_mask[self.bot.blstats.y, self.bot.blstats.x] = 0
        return monster_mask

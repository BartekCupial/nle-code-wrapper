from typing import TYPE_CHECKING

from nle_utils.glyph import G

from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.utils import utils

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


class Pvp:
    def __init__(self, bot: "Bot"):
        self.bot = bot

    def get_monster_mask(self):
        monster_mask = utils.isin(self.bot.glyphs, G.MONS, G.INVISIBLE_MON)
        monster_mask[self.bot.blstats.y, self.bot.blstats.x] = 0
        return monster_mask

    def attack(self, entity: Entity):
        path = self.bot.pathfinder.get_path_to(entity.position)
        orig_path = list(path)
        path = orig_path[1:]

        for point in path:
            if self.bot.pathfinder.distance(self.bot.entity.position, entity.position) > 1:
                self.bot.pathfinder.move(point)
            else:
                self.bot.pathfinder.direction(entity.position)

            # if the enemy is not at original position stop attacking
            # either enemy is dead or it moved
            if len([e for e in self.bot.entities if e.position == entity.position and e.name == entity.name]) == 0:
                return

from nle_code_wrapper.plugins.pvp.attack import attack
from nle_code_wrapper.plugins.pvp.monster_tracker import MonsterTracker


class Pvp:
    def __init__(self, bot):
        self.bot = bot
        self.monster_tracker = MonsterTracker(bot)

    def attack(self, entity):
        return attack(self.bot, entity)

from typing import TYPE_CHECKING

import nle.nethack as nh
from nle_utils.alignment import Alignment
from nle_utils.gender import Gender
from nle_utils.race import Race
from nle_utils.role import Role
from nle_utils.skill import Skill

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


ALL_SPELL_NAMES = [
    "force bolt",
    "drain life",
    "magic missile",
    "cone of cold",
    "fireball",
    "finger of death",
    "protection",
    "create monster",
    "remove curse",
    "create familiar",
    "turn undead",
    "detect monsters",
    "light",
    "detect food",
    "clairvoyance",
    "detect unseen",
    "identify",
    "detect treasure",
    "magic mapping",
    "sleep",
    "confuse monster",
    "slow monster",
    "cause fear",
    "charm monster",
    "jumping",
    "haste self",
    "invisibility",
    "levitation",
    "teleport away",
    "healing",
    "cure blindness",
    "cure sickness",
    "extra healing",
    "stone to flesh",
    "restore ability",
    "knock",
    "wizard lock",
    "dig",
    "polymorph",
    "cancellation",
]

ALL_SPELL_CATEGORIES = [
    "attack",
    "healing",
    "divination",
    "enchantment",
    "clerical",
    "escape",
    "matter",
]


class Property:
    def __init__(self, bot: "Bot"):
        self.bot = bot

    @property
    def confusion(self):
        return "Conf" in bytes(self.bot.tty_chars).decode()

    @property
    def stun(self):
        return "Stun" in bytes(self.bot.tty_chars).decode()

    @property
    def hallu(self):
        return "Hallu" in bytes(self.bot.tty_chars).decode()

    @property
    def blind(self):
        return "Blind" in bytes(self.bot.tty_chars).decode()

    @property
    def polymorph(self):
        if not nh.glyph_is_monster(self.bot.entity.glyph):
            return False
        return self.bot.character.self_glyph != self.bot.entity.glyph


class Character:
    def __init__(self, bot: "Bot"):
        self.bot = bot
        self.prop = Property(bot)
        self.role = None
        self.alignment = None
        self.race = None
        self.gender = None
        self.self_glyph = None
        self.upgradable_skills = dict()

        self.is_lycanthrope = False

    def update(self):
        if "welcome to NetHack!" in self.bot.message:
            self.parse_welcome()
        if "welcome back to NetHack!" in self.bot.message:
            assert False, "game was loaded from save"

        if "You feel feverish." in self.bot.message:
            self.is_lycanthrope = True
        if "You feel purified." in self.bot.message:
            self.is_lycanthrope = False

    @property
    def carrying_capacity(self):
        # TODO: levitation, etc
        return min(1000, (self.bot.blstats.strength_percentage + self.bot.blstats.constitution) * 25 + 50)

    def parse_welcome(self):
        """
        parse agent gender, race, role, alignment form starting message
        """
        self.race = Race.parse(self.bot.message)
        self.gender = Gender.parse(self.bot.message)
        self.role = Role.parse(self.bot.message)
        self.alignment = Alignment.parse(self.bot.message)
        self.skill = Skill.from_role(self.role)
        self.self_glyph = self.bot.entity.glyph

    def __str__(self):
        skill_str = "| ".join(self.skill.get_skill_str_list())
        return (
            "-".join(
                [
                    f"{e.name.lower()[:3]}"
                    for e in [
                        self.role,
                        self.race,
                        self.gender,
                        self.alignment,
                    ]
                ]
            )
            + "\n Skills: "
            + skill_str
        )


if __name__ == "__main__":
    from nle_code_wrapper.envs.nethack.play_nethack import parse_nethack_args, register_nethack_components
    from nle_code_wrapper.utils.tests import create_bot

    register_nethack_components()
    cfg = parse_nethack_args(
        argv=[
            "--env=NetHackScore-v0",
            "--character=@",
            "--no-render",
            "--code_wrapper=False",
        ]
    )
    bot = create_bot(cfg)
    for i in range(1000):
        bot.reset(seed=i)
        str(bot.character)

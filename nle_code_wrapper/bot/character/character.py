from typing import TYPE_CHECKING, Optional

import nle.nethack as nh
import numpy as np
from nle.nethack import actions as A

from nle_code_wrapper.bot.character.properties import Alignment, Gender, Race, Role
from nle_code_wrapper.bot.character.skill import CharacterSkills, Skill
from nle_code_wrapper.bot.inventory import Item

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


class Character:
    def __init__(self, bot: "Bot", character: str):
        self.bot = bot
        self.role = None
        self.alignment = None
        self.race = None
        self.gender = None
        self.upgradable_skills = dict()

        self.is_lycanthrope = False
        self.init = False

        # try to init from character str example: rog-elf-neu-mal
        self.parse_character(character)

    def update(self):
        # 1) try to init from welcome message
        if not self.init:
            if "welcome to NetHack!" in self.bot.message:
                self.parse_welcome(self.bot.message)
            if "welcome back to NetHack!" in self.bot.message:
                assert False, "game was loaded from save"

        # 2) we failed to init from welcome init from attributes
        if not self.init:
            # TODO: fix nle so it doesn't skip at the reset
            obs, *_ = self.bot.env.step(self.bot.env.actions.index(A.Command.ATTRIBUTES))
            message = "\n".join([bytes(line).decode("latin-1") for line in obs["tty_chars"]])
            self.parse_welcome(message)
            obs, *_ = self.bot.env.step(self.bot.env.actions.index(A.Command.ESC))

        if "You feel feverish." in self.bot.message:
            self.is_lycanthrope = True
        if "You feel purified." in self.bot.message:
            self.is_lycanthrope = False

    @property
    def carrying_capacity(self):
        # TODO: levitation, etc
        return min(1000, (self.bot.blstats.strength_percentage + self.bot.blstats.constitution) * 25 + 50)

    def parse_character(self, character):
        if character.split("-") == ["@"]:
            return

        role, race, alignment, gender = character.split("-")
        self.role = Role.from_str(role)
        self.race = Race.from_str(race)
        self.alignment = Alignment.from_str(alignment)
        self.gender = Gender.from_str(gender)
        self.skill = CharacterSkills.from_role(self.role)
        self.init = True

    def parse_welcome(self, message):
        """
        parse agent gender, race, role, alignment form starting message
        """
        self.race = Race.parse(message)
        self.gender = Gender.parse(message)
        self.role = Role.parse(message)
        self.alignment = Alignment.parse(message)
        self.skill = CharacterSkills.from_role(self.role)
        self.init = True

    def get_melee_bonus(self, weapon: Optional[Item] = None):
        """Returns a pair (to_hit, damage) representing combat bonuses

        Args:
            weapon: The weapon being used, or None for unarmed
            monster: Optional monster being attacked TODO:
            large_monster: Whether target is large sized TODO:

        Returns:
            tuple: (to_hit_bonus, damage_bonus)
        """
        # Base to-hit includes luck, ability mods, level (find_roll_to_hit)
        # tmp = 1 + Luck + abon() + find_mac(mtmp) + u.uhitinc
        #     + maybe_polyd(youmonst.data->mlevel, u.ulevel);
        # TODO: add luck?
        to_hit_bonus = 1 + self.abon() + self.bot.blstats.experience_level

        # Calculate damage bonus
        dmg_bonus = self.dbon()  # Strength bonus

        # Monk armor penalties and bonuses (find_roll_to_hit)
        # if (Role_if(PM_MONK) && !Upolyd) {
        #     if (uarm)
        #         tmp -= (*role_roll_penalty = urole.spelarmr);
        #     elif (!uwep && !uarms)
        #         tmp += (u.ulevel / 3) + 2;
        # }
        if self.role == Role.MONK:
            if self.bot.inventory.suit is not None:
                to_hit_bonus -= 20
            elif self.bot.inventory.suit is None and weapon is None:
                monk_bonus = (self.bot.blstats.experience_level // 3) + 2
                to_hit_bonus += monk_bonus

        # Racial bonuses (find_roll_to_hit)
        # if (is_orc(mtmp->data)
        #     && maybe_polyd(is_elf(youmonst.data), Race_if(PM_ELF)))
        #     tmp++;
        # TODO: add target_mon
        # if (target_mon is not None and self.race == Race.ELF and target_mon.is_orc()):
        #     to_hit_bonus += 1

        # if (u.utrap)
        #     tmp -= 3;
        # # TODO: Trapped/stunned penalties
        # if self.bot.character.trapped:
        #     to_hit_bonus -= 3

        # /* encumbrance: with a lot of luggage, your agility diminishes */
        # if ((tmp2 = near_capacity()) != 0)
        #     tmp -= (tmp2 * 2) - 1;
        # TODO: encumbrance
        # enc_penalty = self._get_encumbrance_penalty()
        # if enc_penalty:
        #     to_hit_bonus -= (2 * enc_penalty - 1)

        # /*
        #  * hitval applies if making a weapon attack while wielding a weapon;
        #  * weapon_hit_bonus applies if doing a weapon attack even bare-handed
        #  * or if kicking as martial artist
        #  */
        # if (aatyp == AT_WEAP || aatyp == AT_CLAW) {
        #     if (weapon)
        #         tmp += hitval(weapon, mtmp);
        #     tmp += weapon_hit_bonus(weapon);
        # } else if (aatyp == AT_KICK && martial_bonus()) {
        #     tmp += weapon_hit_bonus((struct obj *) 0);
        # }
        # TODO: hitval returns bonuses against the monster
        # if item:
        #     to_hit_bonus += hitval(item, target_mon)
        skill_hit_bonus, skill_dmg_bonus = self.weapon_skill_bonus(weapon)
        to_hit_bonus += skill_hit_bonus
        dmg_bonus += skill_dmg_bonus

        # TODO: we are missing weapon_damage

        return to_hit_bonus, dmg_bonus

    def get_ranged_bonus(self, launcher: Optional[Item], ammo: Item):
        if launcher is not None:
            assert launcher.is_launcher
            assert ammo.is_firing_projectile
        else:
            assert ammo.is_thrown_projectile

        # Base to-hit includes luck, ability mods, level
        to_hit_bonus = 1 + self.abon() + self.bot.blstats.experience_level

        # Damage bonus does not include strength for launched weapons
        dmg_bonus = 0

        # Racial/role bonuses for certain combinations
        # /* Elves and Samurai do extra damage using
        #  * their bows&arrows; they're highly trained.
        #  */
        # if (Role_if(PM_SAMURAI) && obj->otyp == YA
        #     && uwep->otyp == YUMI)
        #     tmp++;
        # else if (Race_if(PM_ELF) && obj->otyp == ELVEN_ARROW
        #          && uwep->otyp == ELVEN_BOW)
        #     tmp++;
        if launcher and ammo:
            if self.role == Role.SAMURAI and ammo.name == "ya" and launcher.name == "yumi":
                dmg_bonus += 1
            elif self.race == Race.ELF and ammo.name == "elven arrow" and launcher.name == "elven bow":
                dmg_bonus += 1

        # Trapped penalties
        # if (u.utrap)
        #     tmp -= 3;
        # TODO: Add trapped check
        # if self.bot.character.trapped:
        #     to_hit_bonus -= 3

        # Encumbrance penalties
        # TODO: Add encumbrance penalties
        # enc_penalty = self._get_encumbrance_penalty()
        # if enc_penalty:
        #     to_hit_bonus -= (2 * enc_penalty - 1)

        # Add weapon skill bonuses
        skill_hit_bonus, skill_dmg_bonus = self.weapon_skill_bonus(launcher)
        to_hit_bonus += skill_hit_bonus
        dmg_bonus += skill_dmg_bonus

        # TODO: we are missing weapon_damage

        return to_hit_bonus, dmg_bonus

    def abon(self):
        """
        attack bonus for strength & dexterity
        """
        str_stat = self.bot.blstats.strength
        str_perc = self.bot.blstats.strength_percentage
        dex_stat = self.bot.blstats.dexterity
        exp_stat = self.bot.blstats.experience_level

        if str_stat < 6:
            sbon = -2
        elif str_stat < 8:
            sbon = -1
        elif str_stat < 17:
            sbon = 0
        elif str_stat <= 18:
            if str_perc <= 50:
                sbon = 1  # up to 18/50
            else:
                sbon = 2
        else:
            sbon = 3

        # make it a bit easier for a low level character to
        sbon += 1 if (exp_stat < 3) else 0

        if dex_stat < 4:
            return sbon - 3
        elif dex_stat < 6:
            return sbon - 2
        elif dex_stat < 8:
            return sbon - 1
        elif dex_stat < 14:
            return sbon
        else:
            return sbon + dex_stat - 14

    def dbon(self):
        """
        damage bonus for strength
        """
        str_stat = self.bot.blstats.strength
        str_perc = self.bot.blstats.strength_percentage

        if str_stat < 6:
            return -1
        elif str_stat < 16:
            return 0
        elif str_stat < 18:
            return 1
        elif str_stat == 18:
            if str_perc <= 75:
                return 2  # up to 18
            elif str_perc <= 75:
                return 3  # up to 18/75
            elif str_perc <= 90:
                return 4  # up to 18/90
            elif str_perc < 100:
                return 5  # up to 18/99
        else:
            return 6

    def weapon_skill_bonus(self, weapon: Optional[Item]):
        """
        Return hit and damage bonus/penalty based on skill of weapon.
        Treat restricted weapons as unskilled.

        Args:
            weapon: Item object

        Returns:
            Tuple[int]: Hit bonus/penalty, Damage bonus/penalty
        """
        if weapon is None:
            if self.role in (Role.MONK, Role.SAMURAI):
                return self.skill.martial_bonus[self.skill.skill_levels[Skill.BARE_HANDED_COMBAT.value]]
            else:
                return self.skill.unarmed_bonus[self.skill.skill_levels[Skill.BARE_HANDED_COMBAT.value]]

        wep_type = Skill(np.abs(weapon.objects[0].oc_skill))
        return self.skill.weapon_bonus[self.skill.skill_levels[wep_type.value]]

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
        weapon = bot.inventory.main_hand
        bot.character.get_melee_bonus(weapon)

import enum

import numpy as np

from nle_code_wrapper.bot.character.properties import Role


class Skill(enum.Enum):
    # Code to denote that no skill is applicable
    NONE = 0

    # Weapon Skills -- Stephen White
    # Order matters and are used in macros.
    # Positive values denote hand-to-hand weapons or launchers.
    # Negative values denote ammunition or missiles.
    # Update weapon.c if you amend any skills.
    # Also used for oc_subtyp.
    DAGGER = 1
    KNIFE = 2
    AXE = 3
    PICK_AXE = 4
    SHORT_SWORD = 5
    BROAD_SWORD = 6
    LONG_SWORD = 7
    TWO_HANDED_SWORD = 8
    SCIMITAR = 9
    SABER = 10
    CLUB = 11  # Heavy-shafted bludgeon
    MACE = 12
    MORNING_STAR = 13  # Spiked bludgeon
    FLAIL = 14  # Two pieces hinged or chained together
    HAMMER = 15  # Heavy head on the end
    QUARTERSTAFF = 16  # Long-shafted bludgeon
    POLEARMS = 17  # attack two or three steps away
    SPEAR = 18  # includes javelin
    TRIDENT = 19
    LANCE = 20
    BOW = 21  # launchers
    SLING = 22
    CROSSBOW = 23
    DART = 24  # hand-thrown missiles
    SHURIKEN = 25
    BOOMERANG = 26
    WHIP = 27  # flexible, one-handed
    UNICORN_HORN = 28  # last weapon, two-handed

    # Spell Skills added by Larry Stewart-Zerba
    ATTACK_SPELL = 29
    HEALING_SPELL = 30
    DIVINATION_SPELL = 31
    ENCHANTMENT_SPELL = 32
    CLERIC_SPELL = 33
    ESCAPE_SPELL = 34
    MATTER_SPELL = 35

    # Other types of combat
    BARE_HANDED_COMBAT = 36  # actually weaponless; gloves are ok
    TWO_WEAPON_COMBAT = 37  # pair of weapons, one in each hand
    RIDING = 38  # How well you control your steed

    NUM_SKILLS = 39

    @property
    def FIRST_WEAPON(self):
        return Skill.DAGGER

    @property
    def LAST_WEAPON(self):
        return Skill.UNICORN_HORN

    @property
    def FIRST_SPELL(self):
        return Skill.ATTACK_SPELL

    @property
    def LAST_SPELL(self):
        return Skill.MATTER_SPELL

    @property
    def LAST_H_TO_H(self):
        return Skill.RIDING

    @property
    def FIRST_H_TO_H(self):
        return Skill.BARE_HANDED_COMBAT


Skill_A = [
    (Skill.DAGGER, "Basic"),
    (Skill.KNIFE, "Basic"),
    (Skill.PICK_AXE, "Expert"),
    (Skill.SHORT_SWORD, "Basic"),
    (Skill.SCIMITAR, "Skilled"),
    (Skill.SABER, "Expert"),
    (Skill.CLUB, "Skilled"),
    (Skill.QUARTERSTAFF, "Skilled"),
    (Skill.SLING, "Skilled"),
    (Skill.DART, "Basic"),
    (Skill.BOOMERANG, "Expert"),
    (Skill.WHIP, "Expert"),
    (Skill.UNICORN_HORN, "Skilled"),
    (Skill.ATTACK_SPELL, "Basic"),
    (Skill.HEALING_SPELL, "Basic"),
    (Skill.DIVINATION_SPELL, "Expert"),
    (Skill.MATTER_SPELL, "Basic"),
    (Skill.RIDING, "Basic"),
    (Skill.TWO_WEAPON_COMBAT, "Basic"),
    (Skill.BARE_HANDED_COMBAT, "Expert"),
]

Skill_B = [
    (Skill.DAGGER, "Basic"),
    (Skill.AXE, "Expert"),
    (Skill.PICK_AXE, "Skilled"),
    (Skill.SHORT_SWORD, "Expert"),
    (Skill.BROAD_SWORD, "Skilled"),
    (Skill.LONG_SWORD, "Skilled"),
    (Skill.TWO_HANDED_SWORD, "Expert"),
    (Skill.SCIMITAR, "Skilled"),
    (Skill.SABER, "Basic"),
    (Skill.CLUB, "Skilled"),
    (Skill.MACE, "Skilled"),
    (Skill.MORNING_STAR, "Skilled"),
    (Skill.FLAIL, "Basic"),
    (Skill.HAMMER, "Expert"),
    (Skill.QUARTERSTAFF, "Basic"),
    (Skill.SPEAR, "Skilled"),
    (Skill.TRIDENT, "Skilled"),
    (Skill.BOW, "Basic"),
    (Skill.ATTACK_SPELL, "Basic"),
    (Skill.ESCAPE_SPELL, "Basic"),
    (Skill.RIDING, "Basic"),
    (Skill.TWO_WEAPON_COMBAT, "Basic"),
    (Skill.BARE_HANDED_COMBAT, "Master"),
]

Skill_C = [
    (Skill.DAGGER, "Basic"),
    (Skill.KNIFE, "Skilled"),
    (Skill.AXE, "Skilled"),
    (Skill.PICK_AXE, "Basic"),
    (Skill.CLUB, "Expert"),
    (Skill.MACE, "Expert"),
    (Skill.MORNING_STAR, "Basic"),
    (Skill.FLAIL, "Skilled"),
    (Skill.HAMMER, "Skilled"),
    (Skill.QUARTERSTAFF, "Expert"),
    (Skill.POLEARMS, "Skilled"),
    (Skill.SPEAR, "Expert"),
    (Skill.TRIDENT, "Skilled"),
    (Skill.BOW, "Skilled"),
    (Skill.SLING, "Expert"),
    (Skill.ATTACK_SPELL, "Basic"),
    (Skill.MATTER_SPELL, "Skilled"),
    (Skill.BOOMERANG, "Expert"),
    (Skill.UNICORN_HORN, "Basic"),
    (Skill.BARE_HANDED_COMBAT, "Master"),
]

Skill_H = [
    (Skill.DAGGER, "Skilled"),
    (Skill.KNIFE, "Expert"),
    (Skill.SHORT_SWORD, "Skilled"),
    (Skill.SCIMITAR, "Basic"),
    (Skill.SABER, "Basic"),
    (Skill.CLUB, "Skilled"),
    (Skill.MACE, "Basic"),
    (Skill.QUARTERSTAFF, "Expert"),
    (Skill.POLEARMS, "Basic"),
    (Skill.SPEAR, "Basic"),
    (Skill.TRIDENT, "Basic"),
    (Skill.SLING, "Skilled"),
    (Skill.DART, "Expert"),
    (Skill.SHURIKEN, "Skilled"),
    (Skill.UNICORN_HORN, "Expert"),
    (Skill.HEALING_SPELL, "Expert"),
    (Skill.BARE_HANDED_COMBAT, "Basic"),
]

Skill_K = [
    (Skill.DAGGER, "Basic"),
    (Skill.KNIFE, "Basic"),
    (Skill.AXE, "Skilled"),
    (Skill.PICK_AXE, "Basic"),
    (Skill.SHORT_SWORD, "Skilled"),
    (Skill.BROAD_SWORD, "Skilled"),
    (Skill.LONG_SWORD, "Expert"),
    (Skill.TWO_HANDED_SWORD, "Skilled"),
    (Skill.SCIMITAR, "Basic"),
    (Skill.SABER, "Skilled"),
    (Skill.CLUB, "Basic"),
    (Skill.MACE, "Skilled"),
    (Skill.MORNING_STAR, "Skilled"),
    (Skill.FLAIL, "Basic"),
    (Skill.HAMMER, "Basic"),
    (Skill.POLEARMS, "Skilled"),
    (Skill.SPEAR, "Skilled"),
    (Skill.TRIDENT, "Basic"),
    (Skill.LANCE, "Expert"),
    (Skill.BOW, "Basic"),
    (Skill.CROSSBOW, "Skilled"),
    (Skill.ATTACK_SPELL, "Skilled"),
    (Skill.HEALING_SPELL, "Skilled"),
    (Skill.CLERIC_SPELL, "Skilled"),
    (Skill.RIDING, "Expert"),
    (Skill.TWO_WEAPON_COMBAT, "Skilled"),
    (Skill.BARE_HANDED_COMBAT, "Expert"),
]

Skill_Mon = [
    (Skill.QUARTERSTAFF, "Basic"),
    (Skill.SPEAR, "Basic"),
    (Skill.CROSSBOW, "Basic"),
    (Skill.SHURIKEN, "Basic"),
    (Skill.ATTACK_SPELL, "Basic"),
    (Skill.HEALING_SPELL, "Expert"),
    (Skill.DIVINATION_SPELL, "Basic"),
    (Skill.ENCHANTMENT_SPELL, "Basic"),
    (Skill.CLERIC_SPELL, "Skilled"),
    (Skill.ESCAPE_SPELL, "Skilled"),
    (Skill.MATTER_SPELL, "Basic"),
    (Skill.BARE_HANDED_COMBAT, "Grand Master"),
]

Skill_P = [
    (Skill.CLUB, "Expert"),
    (Skill.MACE, "Expert"),
    (Skill.MORNING_STAR, "Expert"),
    (Skill.FLAIL, "Expert"),
    (Skill.HAMMER, "Expert"),
    (Skill.QUARTERSTAFF, "Expert"),
    (Skill.POLEARMS, "Skilled"),
    (Skill.SPEAR, "Skilled"),
    (Skill.TRIDENT, "Skilled"),
    (Skill.LANCE, "Basic"),
    (Skill.BOW, "Basic"),
    (Skill.SLING, "Basic"),
    (Skill.CROSSBOW, "Basic"),
    (Skill.DART, "Basic"),
    (Skill.SHURIKEN, "Basic"),
    (Skill.BOOMERANG, "Basic"),
    (Skill.UNICORN_HORN, "Skilled"),
    (Skill.HEALING_SPELL, "Expert"),
    (Skill.DIVINATION_SPELL, "Expert"),
    (Skill.CLERIC_SPELL, "Expert"),
    (Skill.BARE_HANDED_COMBAT, "Basic"),
]

Skill_R = [
    (Skill.DAGGER, "Expert"),
    (Skill.KNIFE, "Expert"),
    (Skill.SHORT_SWORD, "Expert"),
    (Skill.BROAD_SWORD, "Skilled"),
    (Skill.LONG_SWORD, "Skilled"),
    (Skill.TWO_HANDED_SWORD, "Basic"),
    (Skill.SCIMITAR, "Skilled"),
    (Skill.SABER, "Skilled"),
    (Skill.CLUB, "Skilled"),
    (Skill.MACE, "Skilled"),
    (Skill.MORNING_STAR, "Basic"),
    (Skill.FLAIL, "Basic"),
    (Skill.HAMMER, "Basic"),
    (Skill.POLEARMS, "Basic"),
    (Skill.SPEAR, "Basic"),
    (Skill.CROSSBOW, "Expert"),
    (Skill.DART, "Expert"),
    (Skill.SHURIKEN, "Skilled"),
    (Skill.DIVINATION_SPELL, "Skilled"),
    (Skill.ESCAPE_SPELL, "Skilled"),
    (Skill.MATTER_SPELL, "Skilled"),
    (Skill.RIDING, "Basic"),
    (Skill.TWO_WEAPON_COMBAT, "Expert"),
    (Skill.BARE_HANDED_COMBAT, "Expert"),
]

Skill_Ran = [
    (Skill.DAGGER, "Expert"),
    (Skill.KNIFE, "Skilled"),
    (Skill.AXE, "Skilled"),
    (Skill.PICK_AXE, "Basic"),
    (Skill.SHORT_SWORD, "Basic"),
    (Skill.MORNING_STAR, "Basic"),
    (Skill.FLAIL, "Skilled"),
    (Skill.HAMMER, "Basic"),
    (Skill.QUARTERSTAFF, "Basic"),
    (Skill.POLEARMS, "Skilled"),
    (Skill.SPEAR, "Expert"),
    (Skill.TRIDENT, "Basic"),
    (Skill.BOW, "Expert"),
    (Skill.SLING, "Expert"),
    (Skill.CROSSBOW, "Expert"),
    (Skill.DART, "Expert"),
    (Skill.SHURIKEN, "Skilled"),
    (Skill.BOOMERANG, "Expert"),
    (Skill.WHIP, "Basic"),
    (Skill.HEALING_SPELL, "Basic"),
    (Skill.DIVINATION_SPELL, "Expert"),
    (Skill.ESCAPE_SPELL, "Basic"),
    (Skill.RIDING, "Basic"),
    (Skill.BARE_HANDED_COMBAT, "Basic"),
]

Skill_S = [
    (Skill.DAGGER, "Basic"),
    (Skill.KNIFE, "Skilled"),
    (Skill.SHORT_SWORD, "Expert"),
    (Skill.BROAD_SWORD, "Skilled"),
    (Skill.LONG_SWORD, "Expert"),
    (Skill.TWO_HANDED_SWORD, "Expert"),
    (Skill.SCIMITAR, "Basic"),
    (Skill.SABER, "Basic"),
    (Skill.FLAIL, "Skilled"),
    (Skill.QUARTERSTAFF, "Basic"),
    (Skill.POLEARMS, "Skilled"),
    (Skill.SPEAR, "Skilled"),
    (Skill.LANCE, "Skilled"),
    (Skill.BOW, "Expert"),
    (Skill.SHURIKEN, "Expert"),
    (Skill.ATTACK_SPELL, "Basic"),
    (Skill.DIVINATION_SPELL, "Basic"),
    (Skill.CLERIC_SPELL, "Skilled"),
    (Skill.RIDING, "Skilled"),
    (Skill.TWO_WEAPON_COMBAT, "Expert"),
    (Skill.BARE_HANDED_COMBAT, "Master"),
]

Skill_T = [
    (Skill.DAGGER, "Expert"),
    (Skill.KNIFE, "Skilled"),
    (Skill.AXE, "Basic"),
    (Skill.PICK_AXE, "Basic"),
    (Skill.SHORT_SWORD, "Expert"),
    (Skill.BROAD_SWORD, "Basic"),
    (Skill.LONG_SWORD, "Basic"),
    (Skill.TWO_HANDED_SWORD, "Basic"),
    (Skill.SCIMITAR, "Skilled"),
    (Skill.SABER, "Skilled"),
    (Skill.MACE, "Basic"),
    (Skill.MORNING_STAR, "Basic"),
    (Skill.FLAIL, "Basic"),
    (Skill.HAMMER, "Basic"),
    (Skill.QUARTERSTAFF, "Basic"),
    (Skill.POLEARMS, "Basic"),
    (Skill.SPEAR, "Basic"),
    (Skill.TRIDENT, "Basic"),
    (Skill.LANCE, "Basic"),
    (Skill.BOW, "Basic"),
    (Skill.SLING, "Basic"),
    (Skill.CROSSBOW, "Basic"),
    (Skill.DART, "Expert"),
    (Skill.SHURIKEN, "Basic"),
    (Skill.BOOMERANG, "Basic"),
    (Skill.WHIP, "Basic"),
    (Skill.UNICORN_HORN, "Skilled"),
    (Skill.DIVINATION_SPELL, "Basic"),
    (Skill.ENCHANTMENT_SPELL, "Basic"),
    (Skill.ESCAPE_SPELL, "Skilled"),
    (Skill.RIDING, "Basic"),
    (Skill.TWO_WEAPON_COMBAT, "Skilled"),
    (Skill.BARE_HANDED_COMBAT, "Skilled"),
]

Skill_V = [
    (Skill.DAGGER, "Expert"),
    (Skill.AXE, "Expert"),
    (Skill.PICK_AXE, "Skilled"),
    (Skill.SHORT_SWORD, "Skilled"),
    (Skill.BROAD_SWORD, "Skilled"),
    (Skill.LONG_SWORD, "Expert"),
    (Skill.TWO_HANDED_SWORD, "Expert"),
    (Skill.SCIMITAR, "Basic"),
    (Skill.SABER, "Basic"),
    (Skill.HAMMER, "Expert"),
    (Skill.QUARTERSTAFF, "Basic"),
    (Skill.POLEARMS, "Skilled"),
    (Skill.SPEAR, "Skilled"),
    (Skill.TRIDENT, "Basic"),
    (Skill.LANCE, "Skilled"),
    (Skill.SLING, "Basic"),
    (Skill.ATTACK_SPELL, "Basic"),
    (Skill.ESCAPE_SPELL, "Basic"),
    (Skill.RIDING, "Skilled"),
    (Skill.TWO_WEAPON_COMBAT, "Skilled"),
    (Skill.BARE_HANDED_COMBAT, "Expert"),
]

Skill_W = [
    (Skill.DAGGER, "Expert"),
    (Skill.KNIFE, "Skilled"),
    (Skill.AXE, "Skilled"),
    (Skill.SHORT_SWORD, "Basic"),
    (Skill.CLUB, "Skilled"),
    (Skill.MACE, "Basic"),
    (Skill.QUARTERSTAFF, "Expert"),
    (Skill.POLEARMS, "Skilled"),
    (Skill.SPEAR, "Basic"),
    (Skill.TRIDENT, "Basic"),
    (Skill.SLING, "Skilled"),
    (Skill.DART, "Expert"),
    (Skill.SHURIKEN, "Basic"),
    (Skill.ATTACK_SPELL, "Expert"),
    (Skill.HEALING_SPELL, "Skilled"),
    (Skill.DIVINATION_SPELL, "Expert"),
    (Skill.ENCHANTMENT_SPELL, "Skilled"),
    (Skill.CLERIC_SPELL, "Skilled"),
    (Skill.ESCAPE_SPELL, "Expert"),
    (Skill.MATTER_SPELL, "Expert"),
    (Skill.RIDING, "Basic"),
    (Skill.BARE_HANDED_COMBAT, "Basic"),
]


class CharacterSkills:
    possible_skill_types = ["Fighting Skills", "Weapon Skills", "Spellcasting Skills"]
    possible_skill_levels = ["UnSkilled", "Basic", "Skilled", "Expert", "Master", "Grand Master"]

    SKILL_LEVEL_RESTRICTED = 0
    SKILL_LEVEL_UNSKILLED = 1
    SKILL_LEVEL_BASIC = 2
    SKILL_LEVEL_SKILLED = 3
    SKILL_LEVEL_EXPERT = 4
    SKILL_LEVEL_MASTER = 5
    SKILL_LEVEL_GRAND_MASTER = 6

    weapon_bonus = {
        SKILL_LEVEL_RESTRICTED: (-4, 2),
        SKILL_LEVEL_UNSKILLED: (-4, 2),
        SKILL_LEVEL_BASIC: (0, 0),
        SKILL_LEVEL_SKILLED: (2, 1),
        SKILL_LEVEL_EXPERT: (3, 2),
    }
    two_weapon_bonus = {
        SKILL_LEVEL_RESTRICTED: (-9, -3),
        SKILL_LEVEL_UNSKILLED: (-9, -3),
        SKILL_LEVEL_BASIC: (-7, -1),
        SKILL_LEVEL_SKILLED: (-5, 0),
        SKILL_LEVEL_EXPERT: (-3, 1),
    }
    riding_bonus = {
        SKILL_LEVEL_RESTRICTED: (-2, 0),
        SKILL_LEVEL_UNSKILLED: (-2, 0),
        SKILL_LEVEL_BASIC: (-1, 0),
        SKILL_LEVEL_SKILLED: (0, 1),
        SKILL_LEVEL_EXPERT: (0, 2),
    }
    unarmed_bonus = {
        SKILL_LEVEL_RESTRICTED: (1, 0),
        SKILL_LEVEL_UNSKILLED: (1, 0),
        SKILL_LEVEL_BASIC: (1, 1),
        SKILL_LEVEL_SKILLED: (2, 1),
        SKILL_LEVEL_EXPERT: (2, 2),
        SKILL_LEVEL_MASTER: (3, 2),
        SKILL_LEVEL_GRAND_MASTER: (3, 3),
    }
    martial_bonus = {
        SKILL_LEVEL_RESTRICTED: (1, 0),  # no one has it restricted
        SKILL_LEVEL_UNSKILLED: (2, 1),
        SKILL_LEVEL_BASIC: (3, 3),
        SKILL_LEVEL_SKILLED: (4, 4),
        SKILL_LEVEL_EXPERT: (5, 6),
        SKILL_LEVEL_MASTER: (6, 7),
        SKILL_LEVEL_GRAND_MASTER: (7, 9),
    }

    name_to_skill_level = {
        k: v
        for k, v in zip(
            ["Restricted"] + possible_skill_levels,
            [
                SKILL_LEVEL_RESTRICTED,
                SKILL_LEVEL_UNSKILLED,
                SKILL_LEVEL_BASIC,
                SKILL_LEVEL_SKILLED,
                SKILL_LEVEL_EXPERT,
                SKILL_LEVEL_MASTER,
                SKILL_LEVEL_GRAND_MASTER,
            ],
        )
    }

    name_to_skill_type = {
        # "": Skill.NONE,
        "dagger": Skill.DAGGER,
        "knife": Skill.KNIFE,
        "axe": Skill.AXE,
        "pick-axe": Skill.PICK_AXE,
        "short sword": Skill.SHORT_SWORD,
        "broadsword": Skill.BROAD_SWORD,
        "long sword": Skill.LONG_SWORD,
        "two-handed sword": Skill.TWO_HANDED_SWORD,
        "scimitar": Skill.SCIMITAR,
        "saber": Skill.SABER,
        "club": Skill.CLUB,
        "mace": Skill.MACE,
        "morning star": Skill.MORNING_STAR,
        "flail": Skill.FLAIL,
        "hammer": Skill.HAMMER,
        "quarterstaff": Skill.QUARTERSTAFF,
        "polearms": Skill.POLEARMS,
        "spear": Skill.SPEAR,
        "trident": Skill.TRIDENT,
        "lance": Skill.LANCE,
        "bow": Skill.BOW,
        "sling": Skill.SLING,
        "crossbow": Skill.CROSSBOW,
        "dart": Skill.DART,
        "shuriken": Skill.SHURIKEN,
        "boomerang": Skill.BOOMERANG,
        "whip": Skill.WHIP,
        "unicorn horn": Skill.UNICORN_HORN,
        "attack spells": Skill.ATTACK_SPELL,
        "healing spells": Skill.HEALING_SPELL,
        "divination spells": Skill.DIVINATION_SPELL,
        "enchantment spells": Skill.ENCHANTMENT_SPELL,
        "clerical spells": Skill.CLERIC_SPELL,
        "escape spells": Skill.ESCAPE_SPELL,
        "matter spells": Skill.MATTER_SPELL,
        "bare handed combat": Skill.BARE_HANDED_COMBAT,
        "martial arts": Skill.BARE_HANDED_COMBAT,
        "two weapon combat": Skill.TWO_WEAPON_COMBAT,
        "riding": Skill.RIDING,
    }

    def __init__(self, predefined_skill):
        self.skill_levels = np.zeros(max([v.value for v in self.name_to_skill_type.values()]) + 1, dtype=int)

        # Parse the skill array and set the skill levels
        for skill_entry in predefined_skill:
            skill_type: Skill = skill_entry[0]  # DAGGER, KNIFE, etc.
            skill_level = skill_entry[1]  # Basic, Skilled, etc.
            self.skill_levels[skill_type.value] = self.name_to_skill_level[skill_level]

    @staticmethod
    def from_role(role: Role):
        role_to_skill = {
            Role.ARCHEOLOGIST: Skill_A,
            Role.BARBARIAN: Skill_B,
            Role.CAVEMAN: Skill_C,
            Role.HEALER: Skill_H,
            Role.KNIGHT: Skill_K,
            Role.MONK: Skill_Mon,
            Role.PRIEST: Skill_P,
            Role.RANGER: Skill_Ran,
            Role.ROGUE: Skill_R,
            Role.SAMURAI: Skill_S,
            Role.TOURIST: Skill_T,
            Role.VALKYRIE: Skill_V,
            Role.WIZARD: Skill_W,
        }
        skill = role_to_skill[role]
        return Skill(skill)

    def get_skill_str_list(self):
        inv_skill_type = {v: k for k, v in self.name_to_skill_type.items()}
        inv_skill_level = {v: k for k, v in self.name_to_skill_level.items()}
        return list(
            inv_skill_type[Skill(skill_type)] + "-" + inv_skill_level[level]
            for skill_type, level in enumerate(self.skill_levels)
            if level in inv_skill_level and Skill(skill_type) in inv_skill_type and level != 0
        )

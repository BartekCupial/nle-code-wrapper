import enum


class MonsterClassTypes(enum.Enum):
    S_ANT = 1  # /* a */
    S_BLOB = 2  # /* b */
    S_COCKATRICE = 3  # /* c */
    S_DOG = 4  # /* d */
    S_EYE = 5  # /* e */
    S_FELINE = 6  # /* f: cats */
    S_GREMLIN = 7  # /* g */
    S_HUMANOID = 8  # /* h: small humanoids: hobbit, dwarf */
    S_IMP = 9  # /* i: minor demons */
    S_JELLY = 10  # /* j */
    S_KOBOLD = 11  # /* k */
    S_LEPRECHAUN = 12  # /* l */
    S_MIMIC = 13  # /* m */
    S_NYMPH = 14  # /* n */
    S_ORC = 15  # /* o */
    S_PIERCER = 16  # /* p */
    S_QUADRUPED = 17  # /* q: excludes horses */
    S_RODENT = 18  # /* r */
    S_SPIDER = 19  # /* s */
    S_TRAPPER = 20  # /* t */
    S_UNICORN = 21  # /* u: includes horses */
    S_VORTEX = 22  # /* v */
    S_WORM = 23  # /* w */
    S_XAN = 24  # /* x */
    S_LIGHT = 25  # /* y: yellow light, black light */
    S_ZRUTY = 26  # /* z */
    S_ANGEL = 27  # /* A */
    S_BAT = 28  # /* B */
    S_CENTAUR = 29  # /* C */
    S_DRAGON = 30  # /* D */
    S_ELEMENTAL = 31  # /* E: includes invisible stalker */
    S_FUNGUS = 32  # /* F */
    S_GNOME = 33  # /* G */
    S_GIANT = 34  # /* H: large humanoid: giant, ettin, minotaur */
    S_invisible = 35  # /* I: non-class present in def_monsyms[] */
    S_JABBERWOCK = 36  # /* J */
    S_KOP = 37  # /* K */
    S_LICH = 38  # /* L */
    S_MUMMY = 39  # /* M */
    S_NAGA = 40  # /* N */
    S_OGRE = 41  # /* O */
    S_PUDDING = 42  # /* P */
    S_QUANTMECH = 43  # /* Q */
    S_RUSTMONST = 44  # /* R */
    S_SNAKE = 45  # /* S */
    S_TROLL = 46  # /* T */
    S_UMBER = 47  # /* U: umber hulk */
    S_VAMPIRE = 48  # /* V */
    S_WRAITH = 49  # /* W */
    S_XORN = 50  # /* X */
    S_YETI = 51  # /* Y: includes owlbear, monkey */
    S_ZOMBIE = 52  # /* Z */
    S_HUMAN = 53  # /* @ */
    S_GHOST = 54  # /* <space> */
    S_GOLEM = 55  # /* ' */
    S_DEMON = 56  # /* & */
    S_EEL = 57  # /* ; (fish) */
    S_LIZARD = 58  # /* : (reptiles) */

    S_WORM_TAIL = 59  # /* ~ */
    S_MIMIC_DEF = 60  # /* ] */

    MAXMCLASSES = 61  # /* number of monster classes */

    @staticmethod
    def always_peaceful(monster_name: str):
        always_peaceful = [
            "shopkeeper",
            "guard",
            "prisoner",
            "Oracle",
            "aligned priest",
            "watchman",
            "watch captain",
            "mail daemon",
            "Charon",
        ]

        quest_leaders = [
            "Lord Carnarvon",
            "Pelias",
            "Shaman Karnov",
            "Hippocrates",
            "King Arthur",
            "Grand Master",
            "Arch Priest",
            "Orion",
            "Master of Thieves",
            "Lord Sato",
            "Twoflower",
            "Norn",
            "Neferet the Green",
        ]

        quest_guardians = [
            "student",
            "chieftain",
            "neanderthal",
            "attendant",
            "page",
            "abbot",
            "acolyte",
            "hunter",
            "thug",
            "roshi",
            "guide",
            "warrior",
            "apprentice",
        ]

        return monster_name in always_peaceful + quest_leaders + quest_guardians

    @staticmethod
    def sometimes_peaceful_lawful(monster_name: str):
        sometimes_peaceful = [
            "hobbit",
            "dwarf",
            "dwarf leader",
            "dwarf ruler",
            "tengu",
            "white unicorn",
            "couatl",
            "Aleax",
            "Angel",
            "ki-rin",
            "Archon",
            "giant",
            "stone giant",
            "fire giant",
            "titan",
            "black naga",
            "golden naga",
            "guardian naga",
            "sasquatch",
        ]

        return monster_name in sometimes_peaceful

    @staticmethod
    def sometimes_peaceful_neutral(monster_name: str):
        sometimes_peaceful = [
            "acid blob",
            "little dog",
            "dog",
            "large dog",
            "kitten",
            "housecat",
            "large cat",
            "pony",
            "gray unicorn",
            "horse",
            "warhorse",
            "bat",
            "plains centaur",
            "air elemental",
            "fire elemental",
            "earth elemental",
            "water elemental",
            "gnome",
            "gnome leader",
            "gnomish wizard",
            "gnome ruler",
            "red naga hatchling",
            "black naga hatchling",
            "golden naga hatchling",
            "guardian naga hatchling",
            "garter snake",
            "umber hulk",
            "monkey",
            "ape",
            "human",
            "high cleric",
            "djinni",
        ]

        return monster_name in sometimes_peaceful

    @staticmethod
    def sometimes_peaceful_chaotic(monster_name: str):
        sometimes_peaceful = [
            "gremlin",
            "bugbear",
            "homunculus",
            "imp",
            "quasit",
            "goblin",
            "hobgoblin",
            "orc",
            "hill orc",
            "Mordor orc",
            "Uruk-hai",
            "orc shaman",
            "orc-captain",
            "black unicorn",
            "forest centaur",
            "mountain centaur",
            "hill giant",
            "frost giant",
            "storm giant",
            "red naga",
            "ogre",
            "ogre leader",
            "ogre tyrant",
            "elf",
            "Woodland-elf",
            "Green-elf",
            "Grey-elf",
            "elf-noble",
            "elven monarch",
        ]

        return monster_name in sometimes_peaceful

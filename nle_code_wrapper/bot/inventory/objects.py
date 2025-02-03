from collections import defaultdict

from nle import nethack as nh

from nle_code_wrapper.bot.inventory.properties import ArmorClass, ItemClass

# collect all objects by their class
class_to_objects = defaultdict(list)
for glyph in range(nh.GLYPH_OBJ_OFF, nh.NUM_OBJECTS + nh.GLYPH_OBJ_OFF):
    obj = nh.objclass(nh.glyph_to_obj(glyph))
    obj_class = obj.oc_class
    class_to_objects[obj_class].append(obj)


NAME_TO_OBJECTS = defaultdict(list)
NAME_TO_GLYPHS = defaultdict(list)


def add_obj(key, obj, prefixes=[""], suffixes=[""]):
    assert isinstance(prefixes, list)
    assert isinstance(suffixes, list)
    if key:
        for prefix in prefixes:
            for suffix in suffixes:
                NAME_TO_OBJECTS[prefix + key + suffix].append(obj)


def add_glyph(key, glyph, prefixes=[""], suffixes=[""]):
    assert isinstance(prefixes, list)
    assert isinstance(suffixes, list)
    if key:
        for prefix in prefixes:
            for suffix in suffixes:
                NAME_TO_GLYPHS[prefix + key + suffix].append(glyph)


def add_both(key, obj, glyph, prefixes=[""], suffixes=[""]):
    add_obj(key, obj, prefixes, suffixes)
    add_glyph(key, glyph, prefixes, suffixes)


for glyph in range(nh.GLYPH_OBJ_OFF, nh.NUM_OBJECTS + nh.GLYPH_OBJ_OFF):
    obj_name = ""
    obj_description = ""

    obj = nh.objclass(nh.glyph_to_obj(glyph))
    obj_class = obj.oc_class

    if nh.OBJ_NAME(obj) is not None:
        obj_name = nh.OBJ_NAME(obj)
    if nh.OBJ_DESCR(obj) is not None:
        obj_description = nh.OBJ_DESCR(obj)

    match ItemClass(ord(obj_class)):
        case ItemClass.ILLOBJ:
            add_both(obj_name, obj, glyph)
            add_both(obj_description, obj, glyph)
        case ItemClass.WEAPON:
            add_both(obj_name, obj, glyph)
            add_both(obj_description, obj, glyph)
        case ItemClass.ARMOR:
            match ArmorClass(obj.oc_armcat):
                case ArmorClass.GLOVES:
                    add_both(obj_name, obj, glyph, ["pair of "])
                    shuffle = [
                        "leather gloves",
                        "gauntlets of fumbling",
                        "gauntlets of power",
                        "gauntlets of dexterity",
                    ]
                    if obj_name in shuffle:
                        for obj in class_to_objects[obj_class]:
                            if nh.OBJ_NAME(obj) in shuffle:
                                add_both(obj_description, obj, glyph, ["pair of "])
                    else:
                        add_both(obj_description, obj, glyph, ["pair of "])
                case ArmorClass.BOOTS:
                    add_both(obj_name, obj, glyph, ["pair of "])
                    shuffle = [
                        "speed boots",
                        "water walking boots",
                        "jumping boots",
                        "elven boots",
                        "kicking boots",
                        "fumble boots",
                        "levitation boots",
                    ]
                    if obj_name in shuffle:
                        for obj in class_to_objects[obj_class]:
                            if nh.OBJ_NAME(obj) in shuffle:
                                add_both(obj_description, obj, glyph, ["pair of "])
                    else:
                        add_both(obj_description, obj, glyph, ["pair of "])
                case ArmorClass.CLOAK:
                    add_both(obj_name, obj, glyph)
                    shuffle = [
                        "cloak of protection",
                        "cloak of invisibility",
                        "cloak of magic resistance",
                        "cloak of displacement",
                    ]
                    if obj_name in shuffle:
                        for obj in class_to_objects[obj_class]:
                            if nh.OBJ_NAME(obj) in shuffle:
                                add_both(obj_description, obj, glyph)
                    else:
                        add_both(obj_description, obj, glyph)
                case ArmorClass.HELM:
                    add_both(obj_name, obj, glyph)
                    shuffle = [
                        "helmet",
                        "helm of brilliance",
                        "helm of opposite alignment",
                        "helm of telepathy",
                    ]
                    if obj_name in shuffle:
                        for obj in class_to_objects[obj_class]:
                            if nh.OBJ_NAME(obj) in shuffle:
                                add_both(obj_description, obj, glyph)
                    elif obj_description in [
                        "cornuthaum",
                        "dunce cap",
                    ]:
                        if obj_name in shuffle:
                            for obj in class_to_objects[obj_class]:
                                if nh.OBJ_NAME(obj) in [
                                    "cornuthaum",
                                    "dunce cap",
                                ]:
                                    add_both(obj_description, obj, glyph)
                    else:
                        add_both(obj_description, obj, glyph)
                case _:
                    add_both(obj_name, obj, glyph)
                    add_both(obj_description, obj, glyph)
        case ItemClass.RING:
            add_both(obj_name, obj, glyph, ["ring of "])

            for obj in class_to_objects[obj_class]:
                add_both(obj_description, obj, glyph, suffixes=[" ring"])
        case ItemClass.AMULET:
            if obj_name in ["Amulet of Yendor"]:
                add_both(obj_name, obj, glyph)
            elif obj_description in ["Amulet of Yendor"]:
                add_both(obj_name, obj, glyph)
                add_both(obj_description, obj, glyph)
            else:
                add_both(obj_name, obj, glyph)
                if obj_name not in ["Amulet of Yendor", "cheap plastic imitation of the Amulet of Yendor"]:
                    for obj in class_to_objects[obj_class]:
                        if nh.OBJ_NAME(obj) not in [
                            "Amulet of Yendor",
                            "cheap plastic imitation of the Amulet of Yendor",
                        ]:
                            add_both(obj_description, obj, glyph, suffixes=[" amulet"])
                else:
                    add_both(obj_description, obj, glyph, suffixes=[" amulet"])
        case ItemClass.TOOL:
            if obj_name in ["lenses"]:
                add_both(obj_name, obj, glyph, ["pair of "])
            else:
                add_both(obj_name, obj, glyph)

            add_both(obj_description, obj, glyph)
        case ItemClass.COMESTIBLES:
            add_both(obj_name, obj, glyph)
            add_both(obj_description, obj, glyph)
        case ItemClass.POTION:
            add_both(obj_name, obj, glyph, ["potion of "])
            if obj_name not in ["water"]:
                for obj in class_to_objects[obj_class]:
                    if nh.OBJ_NAME(obj) not in ["water"]:
                        add_both(obj_description, obj, glyph, suffixes=[" potion"])
            else:
                add_both(obj_description, obj, glyph, suffixes=[" potion"])
        case ItemClass.SCROLL:
            add_both(obj_name, obj, glyph, ["scroll of "])
            if obj_name not in ["mail", "blank paper"]:
                for obj in class_to_objects[obj_class]:
                    if nh.OBJ_NAME(obj) not in ["mail", "blank paper"]:
                        add_both(obj_description, obj, glyph, ["scroll labeled "])
            else:
                if obj_description in ["unlabeled"]:
                    add_both(obj_description, obj, glyph, suffixes=[" scroll"])
                else:
                    add_both(obj_description, obj, glyph, ["scroll labeled "])
        case ItemClass.SPELLBOOK:
            if obj_name in ["Book of the Dead", "novel"]:
                add_both(obj_name, obj, glyph)
            else:
                add_both(obj_name, obj, glyph, ["spellbook of "])

            if obj_description in ["paperback"]:
                add_both(obj_description, obj, glyph, suffixes=[" book"])
            else:
                if obj_name not in ["novel", "blank paper", "Book of the Dead"]:
                    for obj in class_to_objects[obj_class]:
                        if nh.OBJ_NAME(obj) not in ["novel", "blank paper", "Book of the Dead"]:
                            add_both(obj_description, obj, glyph, suffixes=[" spellbook"])
                else:
                    add_both(obj_description, obj, glyph, suffixes=[" spellbook"])
        case ItemClass.WAND:
            add_both(obj_name, obj, glyph, ["wand of "])
            for obj in class_to_objects[obj_class]:
                add_both(obj_description, obj, glyph, suffixes=[" wand"])
        case ItemClass.COIN:
            add_both(obj_name, obj, glyph)
            add_both(obj_description, obj, glyph)
        case ItemClass.GEM:
            if obj_name in [
                "luckstone",
                "loadstone",
                "touchstone",
                "rock",
            ]:
                add_both(obj_name, obj, glyph)
                add_both(obj_description, obj, glyph, suffixes=[" stone"])
            elif obj_name in ["flint"]:
                add_both(obj_name, obj, glyph, suffixes=[" stone"])
                add_both(obj_description, obj, glyph, suffixes=[" stone"])
            else:
                add_both(obj_name, obj, glyph)
                add_both(obj_description, obj, glyph, suffixes=[" gem"])
        case ItemClass.ROCK:
            # only boulder and statue
            add_both(obj_name, obj, glyph)
            add_both(obj_description, obj, glyph, suffixes=[" stone"])
        case ItemClass.BALL:
            add_both(obj_name, obj, glyph)  # heavy iron ball
            add_both(obj_name, obj, glyph, ["very "])  # very heavy iron ball
        case ItemClass.CHAIN:
            add_both(obj_name, obj, glyph)  # only iron chain
        case ItemClass.VENOM:
            # only blinding venom, acid venom
            add_both(obj_name, obj, glyph)
            add_both(obj_description, obj, glyph)
        case _:
            add_both(obj_name, obj, glyph)
            add_both(obj_description, obj, glyph)


artifacts = [
    ("Excalibur", "long sword"),
    ("Stormbringer", "runesword"),
    ("Mjollnir", "war hammer"),
    ("Cleaver", "battle-axe"),
    ("Grimtooth", "orcish dagger"),
    ("Orcrist", "elven broadsword"),
    ("Sting", "elven dagger"),
    ("Magicbane", "athame"),
    ("Frost Brand", "long sword"),
    ("Fire Brand", "long sword"),
    ("Dragonbane", "broadsword"),
    ("Demonbane", "long sword"),
    ("Werebane", "silver saber"),
    ("Grayswandir", "silver saber"),
    ("Giantslayer", "long sword"),
    ("Ogresmasher", "war hammer"),
    ("Trollsbane", "morning star"),
    ("Vorpal Blade", "long sword"),
    ("Snickersnee", "katana"),
    ("Sunsword", "long sword"),
    ("The Orb of Detection", "crystal ball"),
    ("The Heart of Ahriman", "luckstone"),
    ("The Sceptre of Might", "mace"),
    ("The Palantir of Westernesse", "crystal ball"),
    ("The Staff of Aesculapius", "quarterstaff"),
    ("The Magic Mirror of Merlin", "mirror"),
    ("The Eyes of the Overworld", "pair of lenses"),
    ("The Mitre of Holiness", "helm of brilliance"),
    ("The Longbow of Diana", "bow"),
    ("The Master Key of Thievery", "skeleton key"),
    ("The Tsurugi of Muramasa", "tsurugi"),
    ("The Platinum Yendorian Express Card", "credit card"),
    ("The Orb of Fate", "crystal ball"),
    ("The Eye of the Aethiopica", "amulet of ESP"),
]

for artifact, appearance in artifacts:
    assert len(NAME_TO_OBJECTS[appearance]) == 1
    for obj in NAME_TO_OBJECTS[appearance]:
        add_obj(artifact, obj, prefixes=["", f"{appearance} named "])

        obj_description = nh.OBJ_DESCR(obj)
        if obj_description:
            match ItemClass(ord(obj.oc_class)):
                case ItemClass.ARMOR:
                    add_obj(artifact, obj, prefixes=["helmet named "])
                case ItemClass.AMULET:
                    add_obj(artifact, obj, prefixes=["amulet named "])
                case ItemClass.GEM:
                    add_obj(artifact, obj, prefixes=[f"{obj_description} stone named "])
                case _:
                    add_obj(artifact, obj, prefixes=[f"{obj_description} named "])


name_to_monsters = {}
for glyph in range(nh.GLYPH_MON_OFF, nh.GLYPH_MON_OFF + nh.NUMMONS):
    permonst = nh.permonst(glyph)
    name_to_monsters[permonst.mname] = permonst


if __name__ == "__main__":

    def not_none(s):
        return s if s is not None else "None"

    for key, objs in NAME_TO_OBJECTS.items():
        # if len(objs) > 1:
        print(key)
        print("\n".join([str((not_none(nh.OBJ_NAME(obj)), not_none(nh.OBJ_DESCR(obj)))) for obj in objs]))
        print("")

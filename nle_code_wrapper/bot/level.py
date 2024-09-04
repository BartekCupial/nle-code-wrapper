from collections import defaultdict

import numpy as np
from nle_utils.glyph import SHOP, C, G

from nle_code_wrapper.utils import utils


class Level:
    def __init__(self, dungeon_number, level_number):
        self.dungeon_number = dungeon_number
        self.level_number = level_number

        self.walkable = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.seen = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.objects = np.zeros((C.SIZE_Y, C.SIZE_X), np.int16)
        self.objects[:] = -1
        self.was_on = np.zeros((C.SIZE_Y, C.SIZE_X), bool)

        self.shop = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.shop_interior = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.shop_type = np.zeros((C.SIZE_Y, C.SIZE_X), np.int32) + SHOP.UNKNOWN

        self.search_count = np.zeros((C.SIZE_Y, C.SIZE_X), np.int32)
        self.door_open_count = np.zeros((C.SIZE_Y, C.SIZE_X), np.int32)

        self.item_disagreement_counter = np.zeros((C.SIZE_Y, C.SIZE_X), np.int32)
        self.items = np.empty((C.SIZE_Y, C.SIZE_X), dtype=object)
        self.items.fill([])
        self.item_count = np.zeros((C.SIZE_Y, C.SIZE_X), dtype=np.int32)

        self.stair_destination = {}  # {(y, x) -> ((dungeon, level), (y, x))}
        self.altars = {}  # {(y, x) -> alignment}

        self.corpses_to_eat = defaultdict(lambda: defaultdict(lambda: -10000))  # {(y, x) -> {monster_id -> age_turn}}

        # ad aerarium -- avoid valut entrance
        self.forbidden = np.zeros((C.SIZE_Y, C.SIZE_X), bool)

    def key(self):
        return (self.dungeon_number, self.level_number)

    @property
    def stairs(self):
        return list(zip(*utils.isin(self.objects, G.STAIR_DOWN).nonzero()))

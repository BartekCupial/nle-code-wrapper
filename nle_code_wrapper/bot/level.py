from collections import defaultdict
from typing import Any, List, Tuple, Union

import numpy as np
from nle import nethack
from nle_utils.blstats import BLStats
from nle_utils.glyph import SHOP, SS, C, G
from numpy import int64, ndarray

from nle_code_wrapper.utils import utils


class Level:
    def __init__(self, dungeon_number: int64, level_number: int64) -> None:
        self.dungeon_number = dungeon_number
        self.level_number = level_number

        self.walkable = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.seen = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.objects = np.zeros((C.SIZE_Y, C.SIZE_X), np.int16)
        self.objects[:] = -1
        self.doors = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.was_on = np.zeros((C.SIZE_Y, C.SIZE_X), bool)

        self.shop = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.shop_interior = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.shop_type = np.zeros((C.SIZE_Y, C.SIZE_X), np.int32) + SHOP.UNKNOWN

        self.search_count = np.zeros((C.SIZE_Y, C.SIZE_X), np.int32)
        self.door_open_count = np.zeros((C.SIZE_Y, C.SIZE_X), np.int32)

        # TODO: we currently do not update what is lying on the floor if we randomly step over sth
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

    def update(self, glyphs: ndarray, blstats: BLStats) -> None:
        if utils.isin(glyphs, G.SWALLOW).any():
            return

        mask = utils.isin(
            glyphs, G.FLOOR, G.STAIR_UP, G.STAIR_DOWN, G.DOOR_OPENED, G.TRAPS, G.ALTAR, G.FOUNTAIN, G.SINK
        )
        self.walkable[mask] = True
        self.seen[mask] = True
        self.objects[mask] = glyphs[mask]

        mask = utils.isin(glyphs, G.MONS, G.PETS, G.BODIES, G.OBJECTS, G.STATUES)
        self.seen[mask] = True
        self.walkable[mask] = True
        doors_closed_mask = utils.isin(self.objects, G.DOOR_CLOSED)
        self.objects[doors_closed_mask & mask] = glyphs[doors_closed_mask & mask] + 2  # from closed to opened doors

        mask = utils.isin(glyphs, G.WALL, G.DOOR_CLOSED, G.BARS)
        self.seen[mask] = True
        self.objects[mask] = glyphs[mask]
        self.walkable[mask] = False

        # TODO: it would be nice if we would change this to False when doors are destroyed
        # how to detect that doors were destroyed
        mask = utils.isin(glyphs, G.DOORS)
        self.doors[mask] = True

        # NOTE: adjust for levitation (1024 in blstats)
        if blstats.prop_mask & nethack.BL_MASK_LEV:
            mask = utils.isin(glyphs, [SS.S_lava])
            self.walkable[mask] = True
            self.seen[mask] = True
        else:
            # make sure to turn back off when we are not levitating
            mask = utils.isin(glyphs, [SS.S_lava])
            self.walkable[mask] = False
            self.seen[mask] = False

        self.was_on[blstats.y, blstats.x] = True

    def object_coords(self, obj: frozenset) -> List[Union[Any, Tuple[int64, int64]]]:
        return utils.coords(self.objects, obj)

    @property
    def stairs(self):
        return self.object_coords(G.STAIR_DOWN)

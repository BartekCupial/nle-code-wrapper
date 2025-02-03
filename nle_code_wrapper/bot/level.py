from collections import defaultdict
from typing import Any, List, Tuple, Union

import numpy as np
from nle import nethack
from nle_utils.blstats import BLStats
from nle_utils.glyph import SHOP, SS, C, G
from numpy import int64, ndarray

from nle_code_wrapper.utils import utils


class SafeAccess:
    def __init__(self, array):
        self.array = array

    def __getitem__(self, key):
        try:
            return self.array[key]
        except IndexError:
            return False


class Level:
    """
    Level class to store information about the current level.
    """

    def __init__(self, dungeon_number: int64, level_number: int64) -> None:
        self.dungeon_number = dungeon_number
        self.level_number = level_number

        self.walkable = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.safe_walkable = SafeAccess(self.walkable)

        self.seen = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.objects = np.zeros((C.SIZE_Y, C.SIZE_X), np.int16)
        self.objects[:] = -1
        self.doors = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.was_on = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.known_traps = np.zeros((C.SIZE_Y, C.SIZE_X), np.int16)
        self.known_traps[:] = -1

        self.shop = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.shop_interior = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.shop_type = np.zeros((C.SIZE_Y, C.SIZE_X), np.int32) + SHOP.UNKNOWN

        self.search_count = np.zeros((C.SIZE_Y, C.SIZE_X), np.int32)
        self.door_open_count = np.zeros((C.SIZE_Y, C.SIZE_X), np.int32)

    def key(self):
        return (self.dungeon_number, self.level_number)

    def update(self, glyphs: ndarray, blstats: BLStats) -> None:
        """
        Update the level with the new glyphs and blstats.
        """
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

        mask = utils.isin(glyphs, G.WALL, G.DOOR_CLOSED, G.BARS, G.BOULDER, frozenset({SS.S_lava, SS.S_water}))
        self.seen[mask] = True
        self.objects[mask] = glyphs[mask]
        self.walkable[mask] = False

        # TODO: it would be nice if we would change this to False when doors are destroyed
        # how to detect that doors were destroyed
        mask = utils.isin(glyphs, G.DOORS)
        self.doors[mask] = True

        mask = utils.isin(glyphs, G.TRAPS)
        self.known_traps[mask] = glyphs[mask]
        self.was_on[blstats.y, blstats.x] = True

    def object_coords(self, obj: frozenset) -> List[Union[Any, Tuple[int64, int64]]]:
        return utils.coords(self.objects, obj)

    @property
    def stairs(self) -> List[Tuple[int64, int64]]:
        """
        Returns the coordinates of the down stairs on the current level.
        """

        return self.object_coords(G.STAIR_DOWN)

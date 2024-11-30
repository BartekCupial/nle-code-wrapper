from typing import Any, Tuple

from nle import nethack
from numpy import int16, int64


class Entity:
    def __init__(self, position: Tuple[int64, int64], glyph: int16) -> None:
        """
        Entity class to represent a monster or player in the game.
        """
        self.position = position
        self.glyph = glyph
        self.name = self.get_monster_name(glyph)

    def get_monster_name(self, glyph: int16) -> str:
        """
        Get the monster name from the glyph.
        """
        if nethack.glyph_is_monster(glyph):
            mon_id = nethack.glyph_to_mon(glyph)
            mon = nethack.permonst(mon_id)
            return mon.mname
        return None

    def __eq__(self, other: Any) -> bool:
        """
        Check if two entities are equal.
        """
        if isinstance(other, Entity):
            return self.position == other.position and self.glyph == other.glyph
        return False

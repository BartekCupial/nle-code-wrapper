from nle import nethack


class Entity:
    def __init__(self, position, glyph):
        self.position = position
        self.glyph = glyph
        self.name = self.get_monster_name(glyph)

    def get_monster_name(self, glyph):
        if nethack.glyph_is_monster(glyph):
            mon_id = nethack.glyph_to_mon(glyph)
            mon = nethack.permonst(mon_id)
            return mon.mname
        return None

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.position == other.position and self.glyph == other.glyph
        return False

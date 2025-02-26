def calc_dps(to_hit, damage):
    return damage * min(20, max(0, (to_hit - 1))) / 20

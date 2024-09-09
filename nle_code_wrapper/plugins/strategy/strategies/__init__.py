from nle_code_wrapper.plugins.strategy.strategies.explore import explore
from nle_code_wrapper.plugins.strategy.strategies.fight_monster import fight_all_monsters, fight_closest_monster
from nle_code_wrapper.plugins.strategy.strategies.goto_stairs import goto_stairs
from nle_code_wrapper.plugins.strategy.strategies.open_door import open_door
from nle_code_wrapper.plugins.strategy.strategies.pray import pray
from nle_code_wrapper.plugins.strategy.strategies.random_move import random_move
from nle_code_wrapper.plugins.strategy.strategies.smart_fight import smart_fight_strategy

__all__ = [
    explore,
    pray,
    goto_stairs,
    fight_closest_monster,
    fight_all_monsters,
    open_door,
    random_move,
    smart_fight_strategy,
]

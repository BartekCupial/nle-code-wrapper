from nle_code_wrapper.bot.strategies.basic_items import (
    apply,
    dip,
    drop,
    eat,
    engrave,
    fire,
    invoke,
    kick,
    loot,
    pickup,
    put_on,
    quaff,
    quiver,
    read,
    remove,
    rub,
    take_off,
    throw,
    wear,
    wield,
    zap,
)
from nle_code_wrapper.bot.strategies.container import loot_container, open_container_key, open_container_kick
from nle_code_wrapper.bot.strategies.cross_lava_river import (
    acquire_levitation,
    cross_lava_river,
    freeze_lava_horn,
    freeze_lava_river,
    freeze_lava_wand,
    levitate_over_lava_river,
)
from nle_code_wrapper.bot.strategies.engrave import engrave_elbereth
from nle_code_wrapper.bot.strategies.explore import (
    explore_corridor,
    explore_corridor_east,
    explore_corridor_north,
    explore_corridor_south,
    explore_corridor_systematically,
    explore_corridor_systematically_east,
    explore_corridor_systematically_north,
    explore_corridor_systematically_south,
    explore_corridor_systematically_west,
    explore_corridor_west,
    explore_room,
    explore_room_east,
    explore_room_north,
    explore_room_south,
    explore_room_systematically,
    explore_room_systematically_east,
    explore_room_systematically_north,
    explore_room_systematically_south,
    explore_room_systematically_west,
    explore_room_west,
)
from nle_code_wrapper.bot.strategies.fight_monster import (
    fight_monster,
    fight_multiple_monsters,
    goto_tactical_position,
    wait_for_monster,
)
from nle_code_wrapper.bot.strategies.goto import (
    goto_corridor,
    goto_corridor_east,
    goto_corridor_north,
    goto_corridor_south,
    goto_corridor_west,
    goto_item,
    goto_room,
    goto_room_east,
    goto_room_north,
    goto_room_south,
    goto_room_west,
    goto_staircase_down,
    goto_staircase_up,
    goto_unexplored_corridor,
    goto_unexplored_room,
)
from nle_code_wrapper.bot.strategies.open_doors import open_doors, open_doors_key, open_doors_kick
from nle_code_wrapper.bot.strategies.pickup import (
    pickup_amulet,
    pickup_armor,
    pickup_boots,
    pickup_cloak,
    pickup_coin,
    pickup_compestibles,
    pickup_gem,
    pickup_gloves,
    pickup_helm,
    pickup_potion,
    pickup_ring,
    pickup_scroll,
    pickup_shield,
    pickup_shirt,
    pickup_spellbook,
    pickup_suit,
    pickup_tool,
    pickup_wand,
    pickup_weapon,
)
from nle_code_wrapper.bot.strategies.push_boulder import (
    align_boulder_for_bridge,
    goto_boulder,
    goto_boulder_closest_to_river,
    push_boulder_east,
    push_boulder_into_river,
    push_boulder_north,
    push_boulder_south,
    push_boulder_west,
)
from nle_code_wrapper.bot.strategies.random_move import random_move
from nle_code_wrapper.bot.strategies.run_away import run_away
from nle_code_wrapper.bot.strategies.search import (
    search_corridor_for_hidden_doors,
    search_for_traps,
    search_room_for_hidden_doors,
)
from nle_code_wrapper.bot.strategies.skill_simple import (
    puton_ring,
    quaff_potion,
    wear_boots,
    wear_cloak,
    wear_gloves,
    wear_helm,
    wear_shield,
    wear_shirt,
    wear_suit,
)
from nle_code_wrapper.bot.strategies.zap_monster import approach_and_zap_monster, approach_monster, zap_monster

__all__ = [
    apply,
    dip,
    drop,
    eat,
    engrave,
    fire,
    kick,
    loot,
    invoke,
    pickup,
    put_on,
    quaff,
    quiver,
    read,
    remove,
    rub,
    take_off,
    throw,
    wear,
    wield,
    zap,
    loot_container,
    open_container_key,
    open_container_kick,
    acquire_levitation,
    cross_lava_river,
    freeze_lava_horn,
    freeze_lava_river,
    freeze_lava_wand,
    levitate_over_lava_river,
    cross_lava_river,
    engrave_elbereth,
    explore_corridor,
    explore_corridor_east,
    explore_corridor_north,
    explore_corridor_south,
    explore_corridor_systematically,
    explore_corridor_systematically_east,
    explore_corridor_systematically_north,
    explore_corridor_systematically_south,
    explore_corridor_systematically_west,
    explore_corridor_west,
    explore_room,
    explore_room_east,
    explore_room_north,
    explore_room_south,
    explore_room_systematically,
    explore_room_systematically_east,
    explore_room_systematically_north,
    explore_room_systematically_south,
    explore_room_systematically_west,
    explore_room_west,
    fight_monster,
    fight_multiple_monsters,
    goto_tactical_position,
    wait_for_monster,
    goto_corridor,
    goto_corridor_east,
    goto_corridor_north,
    goto_corridor_south,
    goto_corridor_west,
    goto_room,
    goto_room_east,
    goto_room_north,
    goto_room_south,
    goto_room_west,
    goto_staircase_down,
    goto_staircase_up,
    goto_unexplored_corridor,
    goto_unexplored_room,
    goto_item,
    open_doors,
    open_doors_kick,
    open_doors_key,
    pickup_amulet,
    pickup_armor,
    pickup_boots,
    pickup_cloak,
    pickup_coin,
    pickup_compestibles,
    pickup_gem,
    pickup_gloves,
    pickup_helm,
    pickup_potion,
    pickup_ring,
    pickup_scroll,
    pickup_shield,
    pickup_shirt,
    pickup_spellbook,
    pickup_suit,
    pickup_tool,
    pickup_wand,
    pickup_weapon,
    puton_ring,
    quaff_potion,
    wear_boots,
    wear_cloak,
    wear_gloves,
    wear_helm,
    wear_shield,
    wear_shirt,
    wear_suit,
    align_boulder_for_bridge,
    goto_boulder,
    goto_boulder_closest_to_river,
    push_boulder_east,
    push_boulder_into_river,
    push_boulder_north,
    push_boulder_south,
    push_boulder_west,
    random_move,
    run_away,
    search_corridor_for_hidden_doors,
    search_for_traps,
    search_room_for_hidden_doors,
    approach_and_zap_monster,
    zap_monster,
    approach_monster,
]

compositional = [
    "apply",
    "dip",
    "drop",
    "eat",
    "engrave",
    "fire",
    "invoke",
    "kick",
    "loot",
    "pickup",
    "put_on",
    "quaff",
    "quiver",
    "read",
    "remove",
    "rub",
    "take_off",
    "throw",
    "wear",
    "wield",
    "zap",
]

container = [
    "loot_container",
    "open_container_key",
    "open_container_kick",
]

cross_lava_river_easy = [
    "acquire_levitation",
    "cross_lava_river",
    "freeze_lava_river",
]

cross_lava_river_hard = [
    "cross_lava_river",
    "approach_lava_river",
    "freeze_lava_horn",
    "freeze_lava_wand",
]

emergency = [
    "engrave_elbereth",
    "random_move",
]

explore = [
    "explore_corridor",
    "explore_corridor_east",
    "explore_corridor_north",
    "explore_corridor_south",
    "explore_corridor_west",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
]

fight_monster_easy = [
    "fight_melee",
    "fight_multiple_monsters",
]

fight_monster_hard = [
    "fight_melee",
    "goto_choke_point",
    "wait_for_monster",
    "run_away",
]

goto = [
    "goto_corridor",
    "goto_corridor_east",
    "goto_corridor_north",
    "goto_corridor_south",
    "goto_corridor_west",
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "goto_unexplored_corridor",
    "goto_unexplored_room",
]

open_doors = ["open_doors", "open_doors_key", "open_doors_kick"]

pickup = [
    "pickup_amulet",
    "pickup_armor",
    "pickup_coin",
    "pickup_food",
    "pickup_gem",
    "pickup_potion",
    "pickup_ring",
    "pickup_scroll",
    "pickup_spellbook",
    "pickup_tool",
    "pickup_wand",
    "pickup_weapon",
    "examine_items",
]

boulder_easy = [
    "goto_boulder",
    "push_boulder_east",
    "push_boulder_north",
    "push_boulder_south",
    "push_boulder_west",
    "align_boulder_for_bridge",
    "goto_boulder_closest_to_river",
    "push_boulder_into_river",
]

boulder_hard = [
    "goto_boulder",
    "push_boulder_east",
    "push_boulder_north",
    "push_boulder_south",
    "push_boulder_west",
]


search = [
    "search_corridor_for_hidden_doors",
    "search_for_traps",
    "search_room_for_hidden_doors",
]

skill_simple = [
    "puton_ring",
    "quaff_potion",
    "wear_boots",
    "wear_cloak",
    "wear_gloves",
    "wear_helm",
    "wear_shield",
    "wear_shirt",
    "wear_suit",
]

zap_monster_easy = [
    "approach_and_zap_monster",
]

zap_monster_hard = ["approach_monster", "zap_monster"]

easy = [
    *cross_lava_river_easy,
    *fight_monster_easy,
    *boulder_easy,
    *zap_monster_easy,
]

hard = [
    *cross_lava_river_hard,
    *fight_monster_hard,
    *boulder_hard,
    *zap_monster_hard,
]

item = [
    *pickup,
    *skill_simple,
]

navigation = [
    *goto,
    *explore,
    *open_doors,
    *search,
]

corridor_battle_easy = [
    "goto_corridor",
    "goto_corridor_east",
    "goto_corridor_north",
    "goto_corridor_south",
    "goto_corridor_west",
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "explore_corridor",
    "explore_corridor_east",
    "explore_corridor_north",
    "explore_corridor_south",
    "explore_corridor_west",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "fight_melee",
    "fight_multiple_monsters",
]

corridor_battle_hard = [
    "goto_corridor",
    "goto_corridor_east",
    "goto_corridor_north",
    "goto_corridor_south",
    "goto_corridor_west",
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "explore_corridor",
    "explore_corridor_east",
    "explore_corridor_north",
    "explore_corridor_south",
    "explore_corridor_west",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "fight_melee",
    "goto_choke_point",
    "wait_for_monster",
    "run_away",
]

corridor = [
    "goto_corridor",
    "goto_corridor_east",
    "goto_corridor_north",
    "goto_corridor_south",
    "goto_corridor_west",
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "explore_corridor",
    "explore_corridor_east",
    "explore_corridor_north",
    "explore_corridor_south",
    "explore_corridor_west",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "open_doors",
    "open_doors_kick",
    "search_corridor_for_hidden_doors",
    "search_room_for_hidden_doors",
]

hideNseek = [
    "goto_corridor",
    "goto_corridor_east",
    "goto_corridor_north",
    "goto_corridor_south",
    "goto_corridor_west",
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "explore_corridor",
    "explore_corridor_east",
    "explore_corridor_north",
    "explore_corridor_south",
    "explore_corridor_west",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "wait_for_monster",
    "run_away",
]

lava_easy = [
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "pickup_amulet",
    "pickup_armor",
    "pickup_coin",
    "pickup_food",
    "pickup_gem",
    "pickup_potion",
    "pickup_ring",
    "pickup_scroll",
    "pickup_spellbook",
    "pickup_tool",
    "pickup_wand",
    "pickup_weapon",
    "acquire_levitation",
    "cross_lava_river",
    "freeze_lava_river",
]

lava_hard = [
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "pickup_amulet",
    "pickup_armor",
    "pickup_coin",
    "pickup_food",
    "pickup_gem",
    "pickup_potion",
    "pickup_ring",
    "pickup_scroll",
    "pickup_spellbook",
    "pickup_tool",
    "pickup_wand",
    "pickup_weapon",
    "cross_lava_river",
    "approach_lava_river",
    "freeze_lava_horn",
    "freeze_lava_wand",
    "puton_ring",
    "quaff_potion",
    "wear_boots",
    "wear_cloak",
    "wear_gloves",
    "wear_helm",
    "wear_shield",
    "wear_shirt",
    "wear_suit",
]

minigrid_easy = [
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "explore_room",
    "open_doors",
    "open_doors_kick",
    "fight_melee",
    "fight_multiple_monsters",
]

minigrid_hard = [
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "explore_room",
    "open_doors",
    "open_doors_kick",
    "fight_melee",
    "goto_choke_point",
    "wait_for_monster",
    "run_away",
]


quest_easy = [
    "goto_corridor",
    "goto_corridor_east",
    "goto_corridor_north",
    "goto_corridor_south",
    "goto_corridor_west",
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "explore_corridor",
    "explore_corridor_east",
    "explore_corridor_north",
    "explore_corridor_south",
    "explore_corridor_west",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "open_doors",
    "open_doors_kick",
    "pickup_amulet",
    "pickup_armor",
    "pickup_coin",
    "pickup_food",
    "pickup_gem",
    "pickup_potion",
    "pickup_ring",
    "pickup_scroll",
    "pickup_spellbook",
    "pickup_tool",
    "pickup_wand",
    "pickup_weapon",
    "acquire_levitation",
    "cross_lava_river",
    "freeze_lava_river",
    "fight_melee",
    "fight_multiple_monsters",
    "approach_and_zap_monster",
]

quest_hard = [
    "goto_corridor",
    "goto_corridor_east",
    "goto_corridor_north",
    "goto_corridor_south",
    "goto_corridor_west",
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "explore_corridor",
    "explore_corridor_east",
    "explore_corridor_north",
    "explore_corridor_south",
    "explore_corridor_west",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "open_doors",
    "open_doors_kick",
    "pickup_amulet",
    "pickup_armor",
    "pickup_coin",
    "pickup_food",
    "pickup_gem",
    "pickup_potion",
    "pickup_ring",
    "pickup_scroll",
    "pickup_spellbook",
    "pickup_tool",
    "pickup_wand",
    "pickup_weapon",
    "cross_lava_river",
    "approach_lava_river",
    "freeze_lava_horn",
    "freeze_lava_wand",
    "puton_ring",
    "quaff_potion",
    "wear_boots",
    "wear_cloak",
    "wear_gloves",
    "wear_helm",
    "wear_shield",
    "wear_shirt",
    "wear_suit",
    "fight_melee",
    "goto_choke_point",
    "wait_for_monster",
    "run_away",
    "approach_monster",
    "zap_monster",
]

river_easy = [
    "descend_stairs",
    "ascend_stairs",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "fight_melee",
    "fight_multiple_monsters",
    "goto_boulder",
    "push_boulder_east",
    "push_boulder_north",
    "push_boulder_south",
    "push_boulder_west",
    "align_boulder_for_bridge",
    "goto_boulder_closest_to_river",
    "push_boulder_into_river",
]

river_hard = [
    "descend_stairs",
    "ascend_stairs",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "fight_melee",
    "goto_choke_point",
    "wait_for_monster",
    "run_away",
    "goto_boulder",
    "push_boulder_east",
    "push_boulder_north",
    "push_boulder_south",
    "push_boulder_west",
]


wod_easy = [
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "pickup_amulet",
    "pickup_armor",
    "pickup_coin",
    "pickup_food",
    "pickup_gem",
    "pickup_potion",
    "pickup_ring",
    "pickup_scroll",
    "pickup_spellbook",
    "pickup_tool",
    "pickup_wand",
    "pickup_weapon",
    "approach_and_zap_monster",
]

wod_hard = [
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "pickup_amulet",
    "pickup_armor",
    "pickup_coin",
    "pickup_food",
    "pickup_gem",
    "pickup_potion",
    "pickup_ring",
    "pickup_scroll",
    "pickup_spellbook",
    "pickup_tool",
    "pickup_wand",
    "pickup_weapon",
    "approach_monster",
    "zap_monster",
]

nethack = [
    # "engrave_identify",
    "loot_container",
    "open_container_key",
    "open_container_kick",
    # "acquire_levitation",
    # "approach_lava_river",
    # "cross_lava_river",
    # "freeze_lava_horn",
    # "freeze_lava_river",
    # "freeze_lava_wand",
    # "levitate_over_lava_river",
    # "cross_lava_river",
    "engrave_elbereth",
    "explore_corridor",
    "explore_corridor_east",
    "explore_corridor_north",
    "explore_corridor_south",
    "explore_corridor_west",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "fight_engulfed",
    "fight_melee",
    "fight_ranged",
    "run_away",
    # "approach_and_zap_monster",
    "zap_monster",
    "approach_monster",
    "fight_multiple_monsters",
    "goto_choke_point",
    "wait_for_monster",
    "goto_corridor",
    "goto_corridor_east",
    "goto_corridor_north",
    "goto_corridor_south",
    "goto_corridor_west",
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "descend_stairs",
    "ascend_stairs",
    "goto_unexplored_corridor",
    "goto_unexplored_room",
    "goto_corpse",
    "examine_items",
    "open_doors",
    "open_doors_kick",
    "open_doors_key",
    "pickup_amulet",
    "pickup_armor",
    "pickup_coin",
    "pickup_food",
    "pickup_gem",
    "pickup_potion",
    "pickup_ring",
    "pickup_scroll",
    "pickup_spellbook",
    "pickup_tool",
    "pickup_wand",
    "pickup_weapon",
    "pickup_corpse",
    "puton_ring",
    "puton_amulet",
    "quaff_potion",
    "quaff_fountain",
    "quaff_sink",
    "read_scroll",
    "pray_altar",
    "zap_wand",
    "wear_boots",
    "wear_cloak",
    "wear_gloves",
    "wear_helm",
    "wear_shield",
    "wear_shirt",
    "wear_suit",
    # "takeoff_shirt",
    # "takeoff_suit",
    # "takeoff_boots",
    # "takeoff_cloak",
    # "takeoff_gloves",
    # "takeoff_helm",
    # "takeoff_shield",
    # "align_boulder_for_bridge",
    "goto_boulder",
    # "goto_boulder_closest_to_river",
    "push_boulder_east",
    # "push_boulder_into_river",
    "push_boulder_north",
    "push_boulder_south",
    "push_boulder_west",
    # "random_move",
    "search_corridor_for_hidden_doors",
    "search_for_traps",
    "search_room_for_hidden_doors",
    "eat_corpse_floor",
    "eat_corpse_inventory",
    "eat_food_inventory",
    # "wield_melee_weapon",
    # "wield_ranged_set",
    "escape_trap",
]

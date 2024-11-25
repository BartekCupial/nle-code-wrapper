import os

from mrunner.helpers.specification_helper import create_experiments_helper

name = globals()["script"][:-3]

# params for all exps
config = {
    "exp_tags": [name],
    "train_for_env_steps": 10_000_000,
    "num_workers": 16,
    "num_envs_per_worker": 32,
    "worker_num_splits": 2,
    "rollout": 32,
    "batch_size": 4096,  # this equals bs = 128, 128 * 32 = 4096
    "penalty_step": -0.001,
    "penalty_time": 0.0,
    "async_rl": True,
    "serial_mode": False,
    "wandb_user": "bartekcupial",
    "wandb_project": "nle_code_wrapper",
    "wandb_group": "ideas-ncbr",
    "with_wandb": True,
    "decorrelate_envs_on_one_worker": False,
    "code_wrapper": True,
    "hierarchical_gamma": True,  # should be the same as code_wrapper
}


strategies = [
    "explore_corridor",
    "explore_corridor_east",
    "explore_corridor_north",
    "explore_corridor_south",
    "explore_corridor_systematically",
    "explore_corridor_systematically_east",
    "explore_corridor_systematically_north",
    "explore_corridor_systematically_south",
    "explore_corridor_systematically_west",
    "explore_corridor_west",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_systematically",
    "explore_room_systematically_east",
    "explore_room_systematically_north",
    "explore_room_systematically_south",
    "explore_room_systematically_west",
    "explore_room_west",
    "explore_items",
    "fight_all_monsters",
    "fight_closest_monster",
    "goto_closest_corridor",
    "goto_closest_corridor_east",
    "goto_closest_corridor_north",
    "goto_closest_corridor_south",
    "goto_closest_corridor_west",
    "goto_closest_room",
    "goto_closest_room_east",
    "goto_closest_room_north",
    "goto_closest_room_south",
    "goto_closest_room_west",
    "goto_closest_staircase_down",
    "goto_closest_staircase_up",
    "goto_closest_unexplored_corridor",
    "goto_closest_unexplored_room",
    "goto_closest_item",
    "open_doors",
    "open_doors_kick",
    "search_corridor_for_hidden_doors",
    "search_room_for_hidden_doors",
]

# params different between exps
params_grid = [
    {
        "seed": list(range(3)),
        "model": ["ChaoticDwarvenGPT5"],
        "strategies": [strategies],
        "gamma": [0.999],
        "restart_behavior": ["overwrite"],
        "env": [env],
        "exp_point": [env],
        "group": [env],
    }
    for env in [
        "MiniHack-Corridor-R2-v0",
        "MiniHack-Corridor-R3-v0",
        "MiniHack-Corridor-R5-v0",
        "MiniHack-CorridorBattle-v0",
        "MiniHack-CorridorBattle-Dark-v0",
        "MiniHack-HideNSeek-v0",
    ]
]


experiments_list = create_experiments_helper(
    experiment_name=name,
    project_name="nle_code_wrapper",
    with_neptune=False,
    script="python3 mrunner_run.py",
    python_path=".",
    tags=[name],
    env={
        "WANDB_API_KEY": os.environ["WANDB_API_KEY"],
    },
    base_config=config,
    params_grid=params_grid,
    mrunner_ignore=".mrunnerignore",
)

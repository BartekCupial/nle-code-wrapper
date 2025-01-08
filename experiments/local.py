import os

from mrunner.helpers.specification_helper import create_experiments_helper

name = globals()["script"][:-3]

# params for all exps
config = {
    "exp_tags": [name],
    "exp_point": "MiniHack-Corridor-R5-v0",
    "train_for_env_steps": 1_000_000,
    "group": "MiniHack-Corridor-R5-v0",
    "num_workers": 1,
    "num_envs_per_worker": 1,
    "worker_num_splits": 1,
    "rollout": 32,
    "batch_size": 256,  # this equals bs = 128, 128 * 32 = 4096
    "penalty_step": -0.001,
    "penalty_time": 0.0,
    "async_rl": True,
    "serial_mode": False,
    "wandb_user": "bartekcupial",
    "wandb_project": "nle_code_wrapper",
    "wandb_group": "ideas-ncbr",
    "with_wandb": False,
    "decorrelate_envs_on_one_worker": False,
    "code_wrapper": True,
}

strategies = [
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
    "goto_staircase_down",
    "goto_staircase_up",
    "goto_unexplored_corridor",
    "goto_unexplored_room",
    "open_doors",
    "open_doors_kick",
    "goto_boulder",
    "push_boulder_east",
    "push_boulder_north",
    "push_boulder_south",
    "push_boulder_west",
    "search_corridor_for_hidden_doors",
    "search_room_for_hidden_doors",
]

# params different between exps
params_grid = [
    {
        "seed": list(range(1)),
        "strategies": [strategies],
        "gamma": [0.999],
        "batch_size": [128],
        "num_workers": [1],
        "num_envs_per_worker": [1],
        "restart_behavior": ["overwrite"],
        "env": [env],
        "exp_point": [env],
        "group": [env],
    }
    for env in [
        "MiniHack-Corridor-R5-v0",
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

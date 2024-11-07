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
    "decorrelate_envs_on_one_worker": True,
    "code_wrapper": True,
    "hierarchical_gamma": True,  # should be the same as code-wrapper
}

# params different between exps
params_grid = [
    {
        "seed": list(range(1)),
        "model": ["default_make_encoder_func", "ScaledNet", "ChaoticDwarvenGPT5"],
        "strategies": [["explore", "search", "open_doors_kick", "goto_stairs", "fight_closest_monster"]],
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
        "MiniHack-KeyRoom-Dark-S5-v0",
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

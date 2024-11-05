import os

from mrunner.helpers.specification_helper import create_experiments_helper

name = globals()["script"][:-3]

# params for all exps
config = {
    "env": "MiniHack-Corridor-R5-v0",
    "exp_tags": [name],
    "exp_point": "corridor5",
    "train_for_env_steps": 1_000_000,
    "group": "corridor5-local",
    "character": "mon-hum-neu-mal",
    "num_workers": 16,
    "num_envs_per_worker": 32,
    "worker_num_splits": 2,
    "rollout": 32,
    "batch_size": 4096,  # this equals bs = 128, 128 * 32 = 4096
    "async_rl": True,
    "serial_mode": False,
    "wandb_user": "bartekcupial",
    "wandb_project": "nle_code_wrapper",
    "wandb_group": "ideas-ncbr",
    "with_wandb": True,
    "decorrelate_envs_on_one_worker": False,
    "code-wrapper": True,
}

# params different between exps
params_grid = [
    {
        "seed": list(range(5)),
        "strategies": [["explore", "search", "open_doors_kick", "goto_stairs", "fight_closest_monster"]],
        "gamma": [0.9, 0.99, 0.999, 1.0],
        "restart_behavior": ["overwrite"],
    },
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

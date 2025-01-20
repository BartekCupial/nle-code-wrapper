import os

from mrunner.helpers.specification_helper import create_experiments_helper

from nle_code_wrapper.utils.granularity import (
    corridor,
    corridor_battle_easy,
    corridor_battle_hard,
    hideNseek,
    lava_easy,
    lava_hard,
    minigrid_easy,
    minigrid_hard,
    quest_easy,
    quest_hard,
    river_easy,
    river_hard,
    wod_easy,
    wod_hard,
)

name = globals()["script"][:-3]

num_minibatches = 1
num_epochs = 1
num_envs = 128
num_steps = 32
num_workers = 16

# params for all exps
config = {
    "exp_tags": [name],
    "run_script": "nle_code_wrapper.agents.sample_factory.minihack.train",
    "train_for_env_steps": 10_000_000,
    "num_workers": num_workers,
    "num_envs_per_worker": num_envs // num_workers,
    "worker_num_splits": 2,
    "rollout": num_steps,
    "batch_size": num_envs * num_steps // num_minibatches,
    "num_batches_per_epoch": num_minibatches,
    "num_epochs": num_epochs,
    "penalty_step": 0.0,
    "penalty_time": 0.0,
    "async_rl": True,
    "serial_mode": False,
    "wandb_user": "bartekcupial",
    "wandb_project": "nle_code_wrapper",
    "wandb_group": "ideas-ncbr",
    "with_wandb": True,
    "decorrelate_envs_on_one_worker": True,
    "code_wrapper": True,
    "hierarchical_gamma": True,  # should be the same as code_wrapper
    "add_letter_strategies": False,
    "add_direction_strategies": False,
    "add_more_strategy": False,
    "max_grad_norm": 40.0,
    "learning_rate": 2e-4,
    "exploration_loss_coeff": 0.001,
    "gamma": 0.999,
    "gae_lambda": 0.95,
    "value_loss_coeff": 0.5,
}

env_groups = [
    (
        corridor,
        "easy",
        [
            "MiniHack-Corridor-R3-v0",
            "MiniHack-Corridor-R5-v0",
            "CustomMiniHack-Corridor-R8-v0",
            "CustomMiniHack-Corridor-R10-v0",
        ],
    ),
    (
        corridor,
        "hard",
        [
            "MiniHack-Corridor-R3-v0",
            "MiniHack-Corridor-R5-v0",
            "CustomMiniHack-Corridor-R8-v0",
            "CustomMiniHack-Corridor-R10-v0",
        ],
    ),
    (
        corridor_battle_easy,
        "easy",
        [
            "MiniHack-CorridorBattle-v0",
            "MiniHack-CorridorBattle-Dark-v0",
        ],
    ),
    (
        corridor_battle_hard,
        "hard",
        [
            "MiniHack-CorridorBattle-v0",
            "MiniHack-CorridorBattle-Dark-v0",
        ],
    ),
    (
        wod_easy,
        "easy",
        [
            "MiniHack-WoD-Hard-Full-v0",
            "MiniHack-WoD-Pro-Full-v0",
        ],
    ),
    (
        wod_hard,
        "hard",
        [
            "MiniHack-WoD-Hard-Full-v0",
            "MiniHack-WoD-Pro-Full-v0",
        ],
    ),
    (
        river_easy,
        "easy",
        [
            "MiniHack-River-v0",
            "MiniHack-River-Monster-v0",
            "MiniHack-River-Lava-v0",
            "MiniHack-River-MonsterLava-v0",
            "MiniHack-River-Narrow-v0",
        ],
    ),
    (
        river_hard,
        "hard",
        [
            "MiniHack-River-v0",
            "MiniHack-River-Monster-v0",
            "MiniHack-River-Lava-v0",
            "MiniHack-River-MonsterLava-v0",
            "MiniHack-River-Narrow-v0",
        ],
    ),
    (
        quest_easy,
        "easy",
        [
            "MiniHack-Quest-Easy-v0",
            "MiniHack-Quest-Medium-v0",
            "MiniHack-Quest-Hard-v0",
        ],
    ),
    (
        quest_hard,
        "hard",
        [
            "MiniHack-Quest-Easy-v0",
            "MiniHack-Quest-Medium-v0",
            "MiniHack-Quest-Hard-v0",
        ],
    ),
    (
        minigrid_easy,
        "easy",
        [
            "MiniHack-MultiRoom-N10-v0",
            "MiniHack-MultiRoom-N6-Locked-v0",
            "MiniHack-MultiRoom-N10-Lava-v0",
            "MiniHack-MultiRoom-N6-Monster-v0",
            "MiniHack-MultiRoom-N6-Extreme-v0",
            "MiniHack-MultiRoom-N6-LavaMonsters-v0",
        ],
    ),
    (
        minigrid_hard,
        "hard",
        [
            "MiniHack-MultiRoom-N10-v0",
            "MiniHack-MultiRoom-N6-Locked-v0",
            "MiniHack-MultiRoom-N10-Lava-v0",
            "MiniHack-MultiRoom-N6-Monster-v0",
            "MiniHack-MultiRoom-N6-Extreme-v0",
            "MiniHack-MultiRoom-N6-LavaMonsters-v0",
        ],
    ),
    (
        lava_easy,
        "easy",
        [
            "MiniHack-Freeze-Lava-Full-v0",
            "MiniHack-LavaCross-Levitate-Full-v0",
            "MiniHack-LavaCross-Full-v0",
        ],
    ),
    (
        lava_hard,
        "hard",
        [
            "MiniHack-Freeze-Lava-Full-v0",
            "MiniHack-LavaCross-Levitate-Full-v0",
            "MiniHack-LavaCross-Full-v0",
        ],
    ),
    (
        hideNseek,
        "easy",
        [
            "MiniHack-HideNSeek-Mapped-v0",
            "MiniHack-HideNSeek-v0",
            "MiniHack-HideNSeek-Lava-v0",
            "MiniHack-HideNSeek-Big-v0",
        ],
    ),
    (
        hideNseek,
        "hard",
        [
            "MiniHack-HideNSeek-Mapped-v0",
            "MiniHack-HideNSeek-v0",
            "MiniHack-HideNSeek-Lava-v0",
            "MiniHack-HideNSeek-Big-v0",
        ],
    ),
]


# params different between exps
params_grid = [
    {
        "seed": list(range(1)),
        "learning_rate": [0.0001],
        "model": ["ChaoticDwarvenGPT5"],
        "strategies": [env_group[0]],
        "restart_behavior": ["overwrite"],
        "env": [env],
        "exp_tags": [f"{name}_{env_group[1]}"],
    }
    for env_group in env_groups
    for env in env_group[2]
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

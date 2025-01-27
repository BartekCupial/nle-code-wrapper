import os

from mrunner.helpers.specification_helper import create_experiments_helper

name = globals()["script"][:-3]

num_minibatches = 1
num_epochs = 1
num_envs = 512
batch_size = 4096
num_steps = 32
num_workers = 16

# params for all exps
config = {
    "exp_tag": name,
    "env": "NetHackScore-v0",
    "run_script": "nle_code_wrapper.agents.sample_factory.minihack.train",
    "train_for_env_steps": 100_000_000,
    "num_workers": num_workers,
    "num_envs_per_worker": num_envs // num_workers,
    "worker_num_splits": 2,
    "rollout": num_steps,
    "batch_size": batch_size,
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
    "max_grad_norm": 40.0,
    "learning_rate": 1e-4,
    "exploration_loss_coeff": 0.001,
    "gamma": 0.999,
    "gae_lambda": 1.0,
    "value_loss_coeff": 1.0,
    "actor_critic_share_weights": True,
    "critic_hidden_dim": 32,
    "critic_depth": 1,
    "actor_hidden_dim": 512,
    "actor_depth": 3,
    "model": "SimBaActorEncoder",
    "add_image_observation": True,
    "normalize_input": False,
    "use_prev_action": True,
    "use_learned_embeddings": True,
    "use_max_pool": True,
    "pixel_size": 1,
    "code_wrapper": False,
    "hierarchical_gamma": False,  # should be the same as code_wrapper
    "add_letter_strategies": False,
    "add_direction_strategies": False,
    "add_more_strategy": False,
}

env_groups = [
    [
        "MiniHack-Corridor-R3-v0",
        "MiniHack-Corridor-R5-v0",
        "CustomMiniHack-Corridor-R8-v0",
        "CustomMiniHack-Corridor-R10-v0",
    ],
    [
        "MiniHack-CorridorBattle-v0",
        "MiniHack-CorridorBattle-Dark-v0",
    ],
    [
        "MiniHack-WoD-Hard-Full-v0",
        "MiniHack-WoD-Pro-Full-v0",
    ],
    [
        "MiniHack-River-v0",
        "MiniHack-River-Monster-v0",
        "MiniHack-River-Lava-v0",
        "MiniHack-River-MonsterLava-v0",
        "MiniHack-River-Narrow-v0",
    ],
    [
        "MiniHack-Quest-Easy-v0",
        "MiniHack-Quest-Medium-v0",
        "MiniHack-Quest-Hard-v0",
    ],
    [
        "MiniHack-MultiRoom-N10-v0",
        "MiniHack-MultiRoom-N6-Locked-v0",
        "MiniHack-MultiRoom-N10-Lava-v0",
        "MiniHack-MultiRoom-N6-Monster-v0",
        "MiniHack-MultiRoom-N6-Extreme-v0",
        "MiniHack-MultiRoom-N6-LavaMonsters-v0",
    ],
    [
        "MiniHack-Freeze-Lava-Full-v0",
        "MiniHack-LavaCross-Levitate-Full-v0",
        "MiniHack-LavaCross-Full-v0",
    ],
    [
        "MiniHack-HideNSeek-Mapped-v0",
        "MiniHack-HideNSeek-v0",
        "MiniHack-HideNSeek-Lava-v0",
        "MiniHack-HideNSeek-Big-v0",
    ],
]

# params different between exps
params_grid = [
    {
        "seed": list(range(1)),
        "env": [env],
    }
    for env_group in env_groups
    for env in env_group
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

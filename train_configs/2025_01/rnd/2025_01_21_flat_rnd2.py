import os

from mrunner.helpers.specification_helper import create_experiments_helper

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
    "train_for_env_steps": 100_000_000,
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
    "code_wrapper": False,
    "max_grad_norm": 40.0,
    "learning_rate": 2e-4,
    "exploration_loss_coeff": 0.001,
    "gamma": 0.999,
    "gae_lambda": 0.95,
    "value_loss_coeff": 0.5,
}


env_groups = [
    [
        "MiniHack-Corridor-R5-v0",
        "CustomMiniHack-Corridor-R10-v0",
    ],
    [
        "MiniHack-Quest-Easy-v0",
        "MiniHack-Quest-Medium-v0",
        "MiniHack-Quest-Hard-v0",
    ],
]

# params different between exps
params_grid = [
    {
        "seed": list(range(3)),
        "learning_rate": [0.0001],
        "model": ["ChaoticDwarvenGPT5"],
        "restart_behavior": ["overwrite"],
        "env": [env],
        "exp_point": [env],
        "group": [env],
        "rnd_int_coef": [0.1],
        "rnd_forward_coef": [0.01],
        "rnd_int_episodic": [True, False],
        "rnd": [True],
    }
    for env_group in env_groups
    for env in env_group
] + [
    {
        "seed": list(range(3)),
        "learning_rate": [0.0001],
        "model": ["ChaoticDwarvenGPT5"],
        "restart_behavior": ["overwrite"],
        "env": [env],
        "exp_point": [env],
        "group": [env],
        "rnd": [False],
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

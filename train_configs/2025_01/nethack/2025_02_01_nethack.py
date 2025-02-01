import os

from mrunner.helpers.specification_helper import create_experiments_helper

from nle_code_wrapper.utils.granularity import nethack

name = globals()["script"][:-3]

num_minibatches = 1
num_epochs = 1
num_envs = 256
batch_size = 4096
num_steps = 32
num_workers = 16

# params for all exps
config = {
    "exp_tag": name,
    "env": "NetHackScore-v0",
    "character": "@",
    "run_script": "nle_code_wrapper.agents.sample_factory.nethack.train",
    "train_for_env_steps": 1_000_000_000,
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
    "code_wrapper": True,
    "hierarchical_gamma": True,  # should be the same as code_wrapper
    "add_letter_strategies": False,
    "add_direction_strategies": False,
    "add_more_strategy": False,
    # specific to this representation
    "model": "NLETerminalCNNEncoder",
    "add_image_observation": True,
    "use_prev_action": True,
    "tokenize_keys": [],
    "obs_keys": ["screen_image", "tty_chars", "tty_colors", "env_steps", "prev_actions"],
}

# params different between exps
params_grid = [
    {
        "seed": list(range(1)),
        "depth": [3],
        "hidden_dim": [512],
        "strategies": [nethack],
        "gamma": [0.999, 0.99],
        "ppo_clip_ratio": [clip_coef],
        "ppo_clip_value": [clip_coef],
        "exploration_loss_coeff": [0.001, 0.01, 0.05, 0.1],
    }
    for clip_coef in [0.1, 0.15, 0.2, 0.25]
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

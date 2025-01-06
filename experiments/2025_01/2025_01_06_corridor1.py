import os

from mrunner.helpers.specification_helper import create_experiments_helper

name = globals()["script"][:-3]

num_minibatches = 4
num_epochs = 4
num_envs = 128
num_steps = 128
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
    "max_strategy_steps": 100,
    "add_letter_strategies": False,
    "add_direction_strategies": False,
    "add_more_strategy": False,
    "max_grad_norm": 40.0,
    "learning_rate": 2e-4,
    "exploration_loss_coeff": 0.001,
    "gamma": 0.999,
    "gae_lambda": 1.0,
    "value_loss_coeff": 0.5,
    "lr_schedule": "linear_decay",
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
        "seed": list(range(3)),
        "learning_rate": [0.0001, 0.0002],
        "model": ["ChaoticDwarvenGPT5"],
        "strategies": [strategies],
        "restart_behavior": ["overwrite"],
        "env": [env],
        "exp_point": [env],
        "group": [env],
    }
    for env in [
        "CustomMiniHack-Corridor-R10-v0",
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

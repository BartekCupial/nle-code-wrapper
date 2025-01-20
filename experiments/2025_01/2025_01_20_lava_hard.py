import os

from mrunner.helpers.specification_helper import create_experiments_helper

from nle_code_wrapper.utils.granularity import hard, item, navigation

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

strategies = [
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "goto_downstairs",
    "goto_upstairs",
    "pickup_amulet",
    "pickup_armor",
    "pickup_coin",
    "pickup_compestibles",
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

# params different between exps
params_grid = [
    {
        "seed": list(range(1)),
        "learning_rate": [0.0001],
        "model": ["ChaoticDwarvenGPT5"],
        "strategies": [strategies],
        "restart_behavior": ["overwrite"],
        "env": [env],
        "exp_point": [env],
        "group": [env],
    }
    for env in [
        "MiniHack-Freeze-Lava-Full-v0",  # cross lava freeze
        "MiniHack-LavaCross-Levitate-Full-v0",  # cross lava levitation
        "MiniHack-LavaCross-Full-v0",  # cross lava freeze or levitation
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

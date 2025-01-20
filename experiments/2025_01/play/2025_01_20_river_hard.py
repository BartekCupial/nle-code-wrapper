import os

from mrunner.helpers.specification_helper import create_experiments_helper

from nle_code_wrapper.utils.granularity import easy, item, navigation

name = globals()["script"][:-3]

num_minibatches = 1
num_epochs = 1
num_envs = 128
num_steps = 32
num_workers = 16

# params for all exps
config = {
    "run_script": "nle_code_wrapper.envs.minihack.play_minihack",
    "code_wrapper": True,
}

strategies = [
    "goto_downstairs",
    "goto_upstairs",
    "explore_room",
    "explore_room_east",
    "explore_room_north",
    "explore_room_south",
    "explore_room_west",
    "fight_monster",
    "goto_choke_point",
    "wait_for_monster",
    "run_away",
    "goto_boulder",
    "push_boulder_east",
    "push_boulder_north",
    "push_boulder_south",
    "push_boulder_west",
]

# params different between exps
params_grid = [
    {
        "strategies": [strategies],
        "env": [env],
    }
    for env in [
        "MiniHack-River-v0",
        "MiniHack-River-Monster-v0",
        "MiniHack-River-Lava-v0",
        "MiniHack-River-MonsterLava-v0",
        "MiniHack-River-Narrow-v0",
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

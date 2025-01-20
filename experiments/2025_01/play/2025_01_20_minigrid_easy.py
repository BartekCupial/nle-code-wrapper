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
    "goto_room",
    "goto_room_east",
    "goto_room_north",
    "goto_room_south",
    "goto_room_west",
    "goto_downstairs",
    "goto_upstairs",
    "explore_room",
    "open_doors",
    "open_doors_kick",
    "fight_monster",
    "fight_multiple_monsters",
]


# params different between exps
params_grid = [
    {
        "strategies": [strategies],
        "env": [env],
    }
    for env in [
        "MiniHack-MultiRoom-N10-v0",
        "MiniHack-MultiRoom-N6-Locked-v0",
        "MiniHack-MultiRoom-N10-Lava-v0",
        "MiniHack-MultiRoom-N6-Monster-v0",
        "MiniHack-MultiRoom-N6-Extreme-v0",
        "MiniHack-MultiRoom-N6-LavaMonsters-v0",
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

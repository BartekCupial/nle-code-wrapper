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
    "acquire_levitation",
    "cross_lava_river",
    "freeze_lava_river",
]


# params different between exps
params_grid = [
    {
        "strategies": [strategies],
        "env": [env],
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

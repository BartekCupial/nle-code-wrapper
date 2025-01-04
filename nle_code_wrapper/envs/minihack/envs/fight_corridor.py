# Copyright (c) Facebook, Inc. and its affiliates.
from minihack import LevelGenerator, MiniHackNavigation
from minihack.envs import register


class CustomMiniHackFightCorridor(MiniHackNavigation):
    def __init__(self, *args, lit=True, **kwargs):
        kwargs["character"] = "kni-hum-law-fem"  # tested on human knight
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 350)

        map = """
-----       ----------------------
|...|       |....................|
|....#######.....................|
|...|       |....................|
-----       ----------------------
"""
        lvl_gen = LevelGenerator(map=map, lit=lit)
        lvl_gen.set_start_rect((1, 1), (3, 3))
        lvl_gen.add_monster(name="giant rat", place=(30, 1))
        lvl_gen.add_monster(name="giant rat", place=(30, 2))
        lvl_gen.add_monster(name="giant rat", place=(30, 3))
        lvl_gen.add_monster(name="giant rat", place=(31, 1))
        lvl_gen.add_monster(name="giant rat", place=(31, 2))
        lvl_gen.add_monster(name="giant rat", place=(31, 3))
        lvl_gen.add_goal_pos((32, 2))
        lvl_gen.add_door("nodoor", (4, 2))
        lvl_gen.add_door("nodoor", (12, 2))

        super().__init__(*args, des_file=lvl_gen.get_des(), **kwargs)


class CustomMiniHackFightCorridorDark(CustomMiniHackFightCorridor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, lit=False, **kwargs)


register(
    id="CustomMiniHack-CorridorBattle-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.fightcorridor:CustomMiniHackFightCorridor",
)

register(
    id="CustomMiniHack-CorridorBattle-Dark-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.fightcorridor:CustomMiniHackFightCorridorDark",
)

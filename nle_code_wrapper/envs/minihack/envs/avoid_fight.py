# Copyright (c) Facebook, Inc. and its affiliates.
from minihack import LevelGenerator, MiniHackNavigation
from minihack.envs import register


class CustomMiniHackAvoidFightStill(MiniHackNavigation):
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
        lvl_gen.add_monster(name="floating eye", place=(29, 2), args=("asleep",))
        lvl_gen.add_monster(name="floating eye", place=(29, 3), args=("asleep",))
        lvl_gen.add_monster(name="floating eye", place=(30, 1), args=("asleep",))
        lvl_gen.add_monster(name="floating eye", place=(30, 3), args=("asleep",))
        lvl_gen.add_monster(name="floating eye", place=(31, 1), args=("asleep",))
        lvl_gen.add_monster(name="floating eye", place=(31, 2), args=("asleep",))
        lvl_gen.add_goal_pos((32, 2))
        lvl_gen.add_door("nodoor", (4, 2))
        lvl_gen.add_door("nodoor", (12, 2))

        super().__init__(*args, des_file=lvl_gen.get_des(), **kwargs)


class CustomMiniHackAvoidFightMoving(MiniHackNavigation):
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
        lvl_gen.add_monster(name="floating eye", place=(29, 2))
        # lvl_gen.add_monster(name="floating eye", place=(29, 3))
        lvl_gen.add_monster(name="floating eye", place=(30, 1))
        # lvl_gen.add_monster(name="floating eye", place=(30, 3))
        lvl_gen.add_monster(name="floating eye", place=(31, 1))
        # lvl_gen.add_monster(name="floating eye", place=(31, 2))
        lvl_gen.add_goal_pos((32, 2))
        lvl_gen.add_door("nodoor", (4, 2))
        lvl_gen.add_door("nodoor", (12, 2))

        super().__init__(*args, des_file=lvl_gen.get_des(), **kwargs)


register(
    id="CustomMiniHack-AvoidFight-Still-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.avoid_fight:CustomMiniHackAvoidFightStill",
)

register(
    id="CustomMiniHack-AvoidFight-Moving-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.avoid_fight:CustomMiniHackAvoidFightMoving",
)

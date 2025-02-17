# Copyright (c) Facebook, Inc. and its affiliates.
from minihack import LevelGenerator, MiniHackNavigation
from minihack.envs import register


class CustomMiniHackReadScroll(MiniHackNavigation):
    def __init__(self, *args, lit=True, **kwargs):
        kwargs["character"] = "kni-hum-law-fem"  # tested on human knight
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 350)
        kwargs["allow_all_yn_questions"] = kwargs.pop("allow_all_yn_questions", True)
        kwargs["allow_all_modes"] = kwargs.pop("allow_all_modes", True)

        map = """
-----       ----------------------
|...|       |....................|
|....#######.....................|
|...|       |....................|
-----       ----------------------
"""
        lvl_gen = LevelGenerator(map=map, lit=lit)
        lvl_gen.set_start_rect((1, 1), (3, 3))
        lvl_gen.add_object("polymorph control", "=", (1, 1))
        lvl_gen.add_object("teleport control", "=", (1, 1))
        lvl_gen.add_object("genocide", "?", (1, 1), cursestate="blessed")
        lvl_gen.add_object("genocide", "?", (1, 1), cursestate="blessed")
        lvl_gen.add_object("genocide", "?", (1, 1), cursestate="uncursed")
        lvl_gen.add_object("genocide", "?", (1, 1), cursestate="uncursed")
        lvl_gen.add_object("teleportation", "?", (1, 1), cursestate="blessed")
        lvl_gen.add_object("identify", "?", (1, 1), cursestate="blessed")
        lvl_gen.add_object("identify", "?", (1, 1), cursestate="uncursed")
        lvl_gen.add_object("charging", "?", (1, 1))
        lvl_gen.add_object("death", "/", (1, 1))

        lvl_gen.add_goal_pos((32, 2))
        lvl_gen.add_door("nodoor", (4, 2))
        lvl_gen.add_door("nodoor", (12, 2))

        super().__init__(*args, des_file=lvl_gen.get_des(), **kwargs)


register(
    id="CustomMiniHack-ReadScroll-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.scroll:CustomMiniHackReadScroll",
)

# Copyright (c) Facebook, Inc. and its affiliates.
from minihack import LevelGenerator, MiniHackNavigation, MiniHackSkill
from minihack.envs import register


class CustomMiniHackEngraveIdentify(MiniHackSkill):
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
        lvl_gen.add_object("cancellation", "/", (1, 1))
        lvl_gen.add_object("cold", "/", (1, 1))
        lvl_gen.add_object("create monster", "/", (1, 1))
        lvl_gen.add_object("death", "/", (1, 1))
        lvl_gen.add_object("digging", "/", (1, 1))
        lvl_gen.add_object("enlightenment", "/", (1, 1))
        lvl_gen.add_object("fire", "/", (1, 1))
        lvl_gen.add_object("light", "/", (1, 1))
        lvl_gen.add_object("lightning", "/", (1, 1))
        lvl_gen.add_object("locking", "/", (1, 1))
        lvl_gen.add_object("magic missile", "/", (1, 1))
        # lvl_gen.add_object("make invisible ", "/", (1, 1))
        lvl_gen.add_object("nothing", "/", (1, 1))
        lvl_gen.add_object("opening", "/", (1, 1))
        # lvl_gen.add_object("polymorph", "/", (1, 1))
        lvl_gen.add_object("probing", "/", (1, 1))
        lvl_gen.add_object("secret door detection", "/", (1, 1))
        # lvl_gen.add_object("sleep ", "/", (1, 1))
        lvl_gen.add_object("slow monster", "/", (1, 1))
        lvl_gen.add_object("speed monster", "/", (1, 1))
        lvl_gen.add_object("striking", "/", (1, 1))
        lvl_gen.add_object("teleportation", "/", (1, 1))
        lvl_gen.add_object("undead turning", "/", (1, 1))
        lvl_gen.add_object("wishing", "/", (1, 1))

        lvl_gen.add_goal_pos((32, 2))
        lvl_gen.add_door("nodoor", (4, 2))
        lvl_gen.add_door("nodoor", (12, 2))

        super().__init__(*args, des_file=lvl_gen.get_des(), **kwargs)


register(
    id="CustomMiniHack-EngraveIdentify-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.engrave_identify:CustomMiniHackEngraveIdentify",
)

from minihack import LevelGenerator, MiniHackSkill, RewardManager
from minihack.envs import register


class MiniHackWoDMelee(MiniHackSkill):
    """Environment for "Wand of death" task."""

    def __init__(self, *args, **kwargs):
        map = """
|----------
|+.........
|----------
"""
        lvl_gen = LevelGenerator(map=map, lit=True)

        lvl_gen.set_start_pos((2, 1))
        kwargs["autopickup"] = kwargs.pop("autopickup", True)
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 50)

        lvl_gen.add_object(name="death", symbol="/", cursestate="blessed", place=((2, 1)))
        lvl_gen.add_monster("minotaur", args=("asleep",), place=(1, 1))

        des_file = lvl_gen.get_des()

        rwrd_mngr = RewardManager()
        rwrd_mngr.add_kill_event("minotaur")

        super().__init__(*args, des_file=des_file, reward_manager=rwrd_mngr, **kwargs)


register(
    id="CustomMiniHack-WoD-Melee-Full-v0",
    entry_point="nle_code_wrapper.envs.custom.envs.skills_wod:MiniHackWoDMelee",
)

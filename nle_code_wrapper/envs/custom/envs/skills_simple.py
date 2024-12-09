from minihack import LevelGenerator, MiniHackSkill, RewardManager
from minihack.envs import register


class MiniHackWearBootsFixed(MiniHackSkill):
    """Environment for "wear" task."""

    def __init__(self, *args, **kwargs):
        lvl_gen = LevelGenerator(w=5, h=5, lit=True)
        lvl_gen.add_object("levitation boots", "[", place=(0, 0))
        lvl_gen.set_start_pos((2, 2))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_wear_event("levitation boots")

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


class MiniHackApplyHornFixed(MiniHackSkill):
    """Environment for "apply" task."""

    def __init__(self, *args, **kwargs):
        lvl_gen = LevelGenerator(w=14, h=14, lit=True)
        lvl_gen.add_object("frost horn", "(", place=(7, 7))
        lvl_gen.set_start_pos((6, 7))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["The bolt of cold bounces!"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


class MiniHackPutOnRingFixed(MiniHackSkill):
    """Environment for "apply" task."""

    def __init__(self, *args, **kwargs):
        lvl_gen = LevelGenerator(w=5, h=5, lit=True)
        lvl_gen.add_object("levitation", "=", place=(0, 0))
        lvl_gen.set_start_pos((2, 2))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["(on right hand)", "(on left hand)"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


class MiniHackZapWandFixed(MiniHackSkill):
    """Environment for "apply" task."""

    def __init__(self, *args, **kwargs):
        lvl_gen = LevelGenerator(w=12, h=12, lit=True)
        lvl_gen.add_object("cold", "/", place=(6, 6))
        lvl_gen.set_start_pos((5, 6))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["The bolt of cold bounces!"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


register(
    id="CustomMiniHack-WearBoots-Fixed-v0",
    entry_point="nle_code_wrapper.envs.custom.envs.skills_simple:MiniHackWearBootsFixed",
)

register(
    id="CustomMiniHack-ApplyHorn-Fixed-v0",
    entry_point="nle_code_wrapper.envs.custom.envs.skills_simple:MiniHackApplyHornFixed",
)

register(
    id="CustomMiniHack-PutOnRing-Fixed-v0",
    entry_point="nle_code_wrapper.envs.custom.envs.skills_simple:MiniHackPutOnRingFixed",
)

register(
    id="CustomMiniHack-ZapWand-Fixed-v0",
    entry_point="nle_code_wrapper.envs.custom.envs.skills_simple:MiniHackZapWandFixed",
)

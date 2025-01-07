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
        reward_manager.add_message_event(["You start to float in the air"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


class MiniHackWearBootsDistr(MiniHackSkill):
    """Environment for "wear" task."""

    def __init__(self, *args, **kwargs):
        lvl_gen = LevelGenerator(w=5, h=5, lit=True)
        lvl_gen.add_object("levitation boots", "[", place=(0, 0))
        lvl_gen.add_object("robe", "[", place=(3, 1))
        lvl_gen.set_start_pos((2, 2))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["You start to float in the air"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


class MiniHackWearSuitFixed(MiniHackSkill):
    """Environment for "wear" task."""

    def __init__(self, *args, **kwargs):
        kwargs["character"] = kwargs.pop("character", "val-hum-new-fem")

        lvl_gen = LevelGenerator(w=5, h=5, lit=True)
        lvl_gen.add_object("plate mail", "[", place=(0, 0))
        lvl_gen.set_start_pos((2, 2))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["The bolt of cold bounces!"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


class MiniHackWearSuitDistr(MiniHackSkill):
    """Environment for "wear" task."""

    def __init__(self, *args, **kwargs):
        kwargs["character"] = kwargs.pop("character", "val-hum-new-fem")

        lvl_gen = LevelGenerator(w=5, h=5, lit=True)
        lvl_gen.add_object("plate mail", "[", place=(0, 0))
        lvl_gen.add_object("levitation boots", "[", place=(1, 0))
        lvl_gen.add_object("dwarvish cloak", "[", place=(2, 0))
        lvl_gen.add_object("Hawaiian shirt", "[", place=(3, 0))
        lvl_gen.set_start_pos((2, 2))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["The bolt of cold bounces!"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


class MiniHackWearSuitSmallPile(MiniHackSkill):
    """Environment for "wear" task."""

    def __init__(self, *args, **kwargs):
        kwargs["character"] = kwargs.pop("character", "val-hum-new-fem")
        kwargs["allow_all_yn_questions"] = kwargs.pop("allow_all_yn_questions", True)
        kwargs["allow_all_modes"] = kwargs.pop("allow_all_modes", True)

        lvl_gen = LevelGenerator(w=5, h=5, lit=True)
        lvl_gen.add_object("booze", "!", place=(0, 0))
        lvl_gen.add_object("levitation boots", "[", place=(0, 0))
        lvl_gen.set_start_pos((2, 2))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["The bolt of cold bounces!"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


class MiniHackWearSuitPile(MiniHackSkill):
    """Environment for "wear" task."""

    def __init__(self, *args, **kwargs):
        kwargs["character"] = kwargs.pop("character", "val-hum-new-fem")
        kwargs["allow_all_yn_questions"] = kwargs.pop("allow_all_yn_questions", True)
        kwargs["allow_all_modes"] = kwargs.pop("allow_all_modes", True)

        lvl_gen = LevelGenerator(w=5, h=5, lit=True)
        lvl_gen.add_object("booze", "!", place=(0, 0))
        lvl_gen.add_object("plate mail", "[", place=(0, 0))
        lvl_gen.add_object("levitation boots", "[", place=(0, 0))
        lvl_gen.add_object("dwarvish cloak", "[", place=(0, 0))
        lvl_gen.add_object("Hawaiian shirt", "[", place=(0, 0))
        lvl_gen.set_start_pos((2, 2))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["The bolt of cold bounces!"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


class MiniHackWearSuitHugePile(MiniHackSkill):
    """Environment for "wear" task."""

    def __init__(self, *args, **kwargs):
        kwargs["character"] = kwargs.pop("character", "val-hum-new-fem")
        kwargs["allow_all_yn_questions"] = kwargs.pop("allow_all_yn_questions", True)
        kwargs["allow_all_modes"] = kwargs.pop("allow_all_modes", True)

        lvl_gen = LevelGenerator(w=5, h=5, lit=True)
        lvl_gen.add_object("booze", "!", place=(0, 0))
        lvl_gen.add_object("plate mail", "[", place=(0, 0))
        lvl_gen.add_object("levitation boots", "[", place=(0, 0))
        for i in range(30):
            lvl_gen.add_object("dwarvish cloak", "[", place=(0, 0))
        lvl_gen.add_object("Hawaiian shirt", "[", place=(0, 0))
        lvl_gen.set_start_pos((2, 2))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["The bolt of cold bounces!"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


class MiniHackWearSuitCloakPile(MiniHackSkill):
    """Environment for "wear" task."""

    def __init__(self, *args, **kwargs):
        kwargs["character"] = kwargs.pop("character", "val-hum-new-fem")
        kwargs["allow_all_yn_questions"] = kwargs.pop("allow_all_yn_questions", True)
        kwargs["allow_all_modes"] = kwargs.pop("allow_all_modes", True)

        lvl_gen = LevelGenerator(w=5, h=5, lit=True)
        for i in range(30):
            lvl_gen.add_object("dwarvish cloak", "[", place=(1, 0))
        lvl_gen.set_start_pos((2, 2))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["The bolt of cold bounces!"])

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


class MiniHackApplyHornDistr(MiniHackSkill):
    """Environment for "apply" task."""

    def __init__(self, *args, **kwargs):
        lvl_gen = LevelGenerator(w=14, h=14, lit=True)
        lvl_gen.add_object("frost horn", "(", place=(7, 7))
        lvl_gen.add_object("skeleton key", "(", place=(5, 4))
        lvl_gen.set_start_pos((3, 4))
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


class MiniHackQuaffPotionFixed(MiniHackSkill):
    """Environment for "apply" task."""

    def __init__(self, *args, **kwargs):
        lvl_gen = LevelGenerator(w=5, h=5, lit=True)
        lvl_gen.add_object("levitation", "!", place=(0, 0))
        lvl_gen.set_start_pos((2, 2))
        des_file = lvl_gen.get_des()

        reward_manager = RewardManager()
        reward_manager.add_message_event(["You start to float in the air"])

        super().__init__(*args, des_file=des_file, reward_manager=reward_manager, **kwargs)


register(
    id="CustomMiniHack-WearBoots-Fixed-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackWearBootsFixed",
)

register(
    id="CustomMiniHack-WearBoots-Distr-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackWearBootsDistr",
)

register(
    id="CustomMiniHack-WearSuit-Fixed-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackWearSuitFixed",
)

register(
    id="CustomMiniHack-WearSuit-Distr-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackWearSuitDistr",
)

register(
    id="CustomMiniHack-WearSuit-SmallPile-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackWearSuitSmallPile",
)

register(
    id="CustomMiniHack-WearSuit-Pile-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackWearSuitPile",
)

register(
    id="CustomMiniHack-WearSuit-HugePile-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackWearSuitHugePile",
)

register(
    id="CustomMiniHack-WearSuit-CloakPile-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackWearSuitCloakPile",
)

register(
    id="CustomMiniHack-ApplyHorn-Fixed-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackApplyHornFixed",
)

register(
    id="CustomMiniHack-ApplyHorn-Distr-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackApplyHornDistr",
)

register(
    id="CustomMiniHack-PutOnRing-Fixed-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackPutOnRingFixed",
)

register(
    id="CustomMiniHack-ZapWand-Fixed-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackZapWandFixed",
)

register(
    id="CustomMiniHack-QuaffPotion-Fixed-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.skills_simple:MiniHackQuaffPotionFixed",
)

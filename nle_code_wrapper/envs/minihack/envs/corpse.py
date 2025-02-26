from minihack.envs import register
from minihack.envs.keyroom import MiniHackKeyDoor


class CustomMiniHackCorpse(MiniHackKeyDoor):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 100)
        kwargs["allow_all_yn_questions"] = kwargs.pop("allow_all_yn_questions", True)
        kwargs["allow_all_modes"] = kwargs.pop("allow_all_modes", True)
        super().__init__(*args, des_file="nle_code_wrapper/envs/minihack/dat/corpse.des", **kwargs)


register(
    id="CustomMiniHack-Corpse-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.corpse:CustomMiniHackCorpse",
)

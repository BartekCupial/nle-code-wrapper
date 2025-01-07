from minihack.envs import register
from minihack.envs.keyroom import MiniHackKeyDoor


class CustomMiniHackChest(MiniHackKeyDoor):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 100)
        super().__init__(*args, des_file="nle_code_wrapper/envs/minihack/dat/chest.des", **kwargs)


register(
    id="CustomMiniHack-Chest-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.chest:CustomMiniHackChest",
)

from minihack import MiniHack
from minihack.base import MH_DEFAULT_OBS_KEYS
from minihack.envs import register
from nle.nethack import USEFUL_ACTIONS


class CustomMiniHackKeyRoom(MiniHack):
    def __init__(self, *args, **kwargs):
        # Play with Caveman character by default
        kwargs["character"] = kwargs.pop("character", "cav-hum-neu-mal")
        # Default episode limit
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 250)
        default_keys = MH_DEFAULT_OBS_KEYS + [
            "inv_strs",
            "inv_letters",
        ]
        kwargs["observation_keys"] = kwargs.pop("observation_keys", default_keys)
        super().__init__(*args, actions=USEFUL_ACTIONS, **kwargs)


class CustomMiniHackKeyDoor(CustomMiniHackKeyRoom):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, des_file="nle_code_wrapper/envs/minihack/dat/key_and_door.des", **kwargs)


class CustomMiniHackKeyWandDoor(CustomMiniHackKeyRoom):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, des_file="nle_code_wrapper/envs/minihack/dat/key_wand_and_door.des", **kwargs)


register(
    id="CustomMiniHack-KeyDoor-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.key_room_items:CustomMiniHackKeyDoor",
)

register(
    id="CustomMiniHack-KeyWandDoor-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.key_room_items:CustomMiniHackKeyWandDoor",
)

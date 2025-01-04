from minihack.envs import register
from minihack.envs.corridor import MiniHackCorridor


class CustomMiniHackCorridor8(MiniHackCorridor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, des_file="corridor8.des", **kwargs)


class CustomMiniHackCorridor10(MiniHackCorridor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, des_file="corridor10.des", **kwargs)


register(
    id="CustomMiniHack-Corridor-R8-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.corridor:CustomMiniHackCorridor8",
)
register(
    id="CustomMiniHack-Corridor-R10-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.corridor:CustomMiniHackCorridor10",
)

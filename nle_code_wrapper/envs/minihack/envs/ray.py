from minihack import MiniHackSkill
from minihack.envs import register


class MiniHackRayStraight(MiniHackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, des_file="nle_code_wrapper/envs/minihack/dat/ray_straight.des", **kwargs)


class MiniHackRayAngled(MiniHackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, des_file="nle_code_wrapper/envs/minihack/dat/ray_angled.des", **kwargs)


class MiniHackRayConvexCorner(MiniHackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, des_file="nle_code_wrapper/envs/minihack/dat/ray_convex_corner.des", **kwargs)


register(
    id="CustomMiniHack-RayStraight-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.ray:MiniHackRayStraight",
)

register(
    id="CustomMiniHack-RayAngled-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.ray:MiniHackRayAngled",
)

register(
    id="CustomMiniHack-RayConvexCorner-v0",
    entry_point="nle_code_wrapper.envs.minihack.envs.ray:MiniHackRayConvexCorner",
)

import pytest

from nle_code_wrapper.envs.custom.play_custom import parse_custom_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestRaySimulator:
    @pytest.mark.parametrize("env", ["CustomMiniHack-RayStraight-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_ray_straight(self, env, seed):
        cfg = parse_custom_args(
            argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False", "--autopickup=True"]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        hit_targets = bot.pvp.ray_simulator.simulate_ray(bot.entity.position, (-1, 0))
        assert len(hit_targets) == 1
        assert hit_targets[bot.entity.position] == 1.0

    @pytest.mark.parametrize("env", ["CustomMiniHack-RayAngled-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_ray_angled(self, env, seed):
        cfg = parse_custom_args(
            argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False", "--autopickup=True"]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        hit_targets = bot.pvp.ray_simulator.simulate_ray(bot.entity.position, (-1, -1))
        assert len(hit_targets) == 2

    @pytest.mark.parametrize("env", ["CustomMiniHack-RayStraight-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_ray_concave_corner(self, env, seed):
        cfg = parse_custom_args(
            argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False", "--autopickup=True"]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        hit_targets = bot.pvp.ray_simulator.simulate_ray(bot.entity.position, (-1, -1))
        assert len(hit_targets) == 1
        assert hit_targets[bot.entity.position] == 1.0

    @pytest.mark.parametrize("env", ["CustomMiniHack-RayConvexCorner-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_ray_convex_corner(self, env, seed):
        cfg = parse_custom_args(
            argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False", "--autopickup=True"]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        hit_targets = bot.pvp.ray_simulator.simulate_ray(bot.entity.position, (-1, -1))
        assert len(hit_targets) == 3

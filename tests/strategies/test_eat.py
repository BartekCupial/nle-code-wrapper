import pytest

from nle_code_wrapper.bot.strategies import (
    eat_corpse_floor,
    eat_corpse_inventory,
    eat_food_inventory,
    pickup_corpse,
    pickup_food,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestEat:
    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-Corpse-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(2)))
    def test_eat_corpse_floor(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_food(bot)
        assert eat_corpse_floor(bot)

    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-Corpse-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(2)))
    def test_eat_corpse_inventory(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_corpse(bot)
        pickup_food(bot)
        assert eat_corpse_inventory(bot)

    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-Corpse-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(3)))
    def test_eat_food_inventory(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                # "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_corpse(bot)
        pickup_food(bot)
        assert eat_food_inventory(bot)

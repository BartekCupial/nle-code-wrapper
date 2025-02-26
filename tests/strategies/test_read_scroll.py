import pytest

from nle_code_wrapper.bot.strategies import (
    goto_corridor,
    goto_room,
    pickup_ring,
    pickup_scroll,
    puton_ring,
    read_scroll,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestEngraveIdentify:
    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-ReadScroll-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(3)))
    def test_engrave(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--autopickup=True",
                "--code_wrapper=False",
                "--max_strategy_steps=1000",
            ]
        )

        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_ring(bot)
        pickup_scroll(bot)
        goto_corridor(bot)
        goto_room(bot)
        puton_ring(bot)
        puton_ring(bot)
        while read_scroll(bot):
            pass

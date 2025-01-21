import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategies import goto_downstairs
from nle_code_wrapper.bot.strategies.pickup import pickup_potion, pickup_ring
from nle_code_wrapper.bot.strategies.skill_simple import puton_ring, quaff_potion
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


def solve(bot: "Bot"):
    while True:
        if pickup_potion(bot):
            pass
        elif pickup_ring(bot):
            pass

        if quaff_potion(bot):
            goto_downstairs(bot)
        elif puton_ring(bot):
            goto_downstairs(bot)


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-LavaCross-Levitate-Potion-Inv-Full-v0",
            "MiniHack-LavaCross-Levitate-Ring-Inv-Full-v0",
            "MiniHack-LavaCross-Levitate-Potion-Pickup-Full-v0",
            "MiniHack-LavaCross-Levitate-Ring-Pickup-Full-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(5)))
    def test_lava(self, env, seed):
        # TODO: for some of the variants there are monsters which have to be dealt with
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )
        cfg.strategies = [solve]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

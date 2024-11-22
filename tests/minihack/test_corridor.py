import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import (
    general_explore,
    general_search,
    goto_closest_staircase_down,
    open_doors,
    open_doors_kick,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize("env", ["MiniHack-Corridor-R3-v0"])
    @pytest.mark.parametrize("seed", [0, 1])
    def test_corridor_open_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])

        def general_solve(bot: "Bot"):
            while True:
                for strategy in [goto_closest_staircase_down, open_doors_kick, general_explore]:
                    try:
                        strategy(bot)
                    except BotPanic:
                        pass

        cfg.strategies = [general_solve]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize("env", ["MiniHack-Corridor-R2-v0"])
    @pytest.mark.parametrize("seed", [7])
    def test_corridor_closed_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])

        def general_kick(bot: "Bot"):
            while True:
                try:
                    if goto_closest_staircase_down(bot):
                        pass
                    elif open_doors(bot):
                        open_doors_kick(bot)
                    else:
                        general_explore(bot)
                except BotPanic:
                    pass

        cfg.strategies = [general_kick]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize("env", ["MiniHack-Corridor-R3-v0"])
    @pytest.mark.parametrize("seed", [9])
    def test_corridor_hidden_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])

        def general_kick(bot: "Bot"):
            while True:
                try:
                    if goto_closest_staircase_down(bot):
                        pass
                    elif open_doors(bot):
                        open_doors_kick(bot)
                    elif general_explore(bot):
                        pass
                    else:
                        general_search(bot)
                except BotPanic:
                    pass

        cfg.strategies = [general_kick]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

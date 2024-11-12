import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import explore, goto_stairs, open_doors, open_doors_kick, search
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize("env", ["MiniHack-Corridor-R3-v0"])
    @pytest.mark.parametrize("seed", [0, 1])
    def test_corridor_open_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        cfg.strategies = [open_doors, goto_stairs, explore]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize("env", ["MiniHack-Corridor-R2-v0"])
    @pytest.mark.parametrize("seed", [7])
    def test_corridor_closed_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])

        def general_kick(bot: "Bot"):
            while True:
                try:
                    if goto_stairs(bot):
                        pass
                    elif open_doors(bot):
                        open_doors_kick(bot)
                    else:
                        explore(bot)
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
                    if goto_stairs(bot):
                        pass
                    elif open_doors(bot):
                        open_doors_kick(bot)
                    elif explore(bot):
                        pass
                    else:
                        search(bot)
                except BotPanic:
                    pass

        cfg.strategies = [general_kick]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

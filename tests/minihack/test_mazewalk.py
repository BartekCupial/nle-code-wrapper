import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategy import Strategy
from nle_code_wrapper.bot.strategy.strategies import explore, goto_stairs
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-MazeWalk-9x9-v0",
            "MiniHack-MazeWalk-Mapped-9x9-v0",
            "MiniHack-MazeWalk-15x15-v0",
            "MiniHack-MazeWalk-Mapped-15x15-v0",
            "MiniHack-MazeWalk-45x19-v0",
            "MiniHack-MazeWalk-Mapped-45x19-v0",
        ],
    )
    def test_solve_mazewalk(self, env):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render"])

        @Strategy.wrap
        def general_explore(bot: "Bot"):
            stairs_strat = goto_stairs(bot)
            explore_strat = explore(bot)

            while True:
                try:
                    if stairs_strat():
                        pass
                    else:
                        explore_strat()
                except BotPanic:
                    pass
                yield True

        cfg.strategies = [general_explore]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import general_explore, goto_stairs
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-ExploreMaze-Easy-v0",
            "MiniHack-ExploreMaze-Easy-Mapped-v0",
            "MiniHack-ExploreMaze-Hard-v0",
            "MiniHack-ExploreMaze-Hard-Mapped-v0",
            "MiniHack-Labyrinth-Small-v0",
        ],
    )
    def test_solve_explore(self, env):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render"])

        def solve(bot: "Bot"):
            while True:
                try:
                    if goto_stairs(bot):
                        pass
                    else:
                        general_explore(bot)
                except BotPanic:
                    pass

        cfg.strategies = [solve]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

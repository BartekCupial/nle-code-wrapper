import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import explore_room, goto_closest_staircase_down
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

        def solve(bot: "Bot"):
            while True:
                try:
                    if goto_closest_staircase_down(bot):
                        pass
                    else:
                        explore_room(bot)
                except BotPanic:
                    pass

        cfg.strategies = [solve]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

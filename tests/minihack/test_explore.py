import pytest

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategy import Strategy
from nle_code_wrapper.bot.strategy.strategies import explore, goto_stairs
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.play import play


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "explore_easy",
            "explore_easy_map",
            "explore_hard",
            "explore_hard_map",
        ],
    )
    def test_solve_explore(self, env):
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

        status = play(cfg, strategies=[general_explore])
        assert status == "TASK_SUCCESSFUL"

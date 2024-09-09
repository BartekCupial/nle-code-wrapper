import pytest

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.plugins.strategy import Strategy
from nle_code_wrapper.plugins.strategy.strategies import explore, goto_stairs


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
    def test_solve_mazewalk(self, env):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render"])
        bot = Bot(cfg)

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

        bot.strategy(general_explore)
        status = bot.main()
        assert status == bot.env.StepStatus.TASK_SUCCESSFUL

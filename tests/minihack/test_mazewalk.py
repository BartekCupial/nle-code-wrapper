import pytest

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.minihack.run_minihack import parse_minihack_args
from nle_code_wrapper.strategies import explore, goto_stairs, kill_all_monsters


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
        bot.strategy(kill_all_monsters)
        bot.strategy(goto_stairs)
        bot.strategy(explore)
        assert bot.main()

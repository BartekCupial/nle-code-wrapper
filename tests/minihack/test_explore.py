from functools import partial

import pytest

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.minihack.run_minihack import parse_minihack_args
from nle_code_wrapper.strategies import find_stairs


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
        bot = Bot(cfg)

        bot.global_strategy = partial(find_stairs, bot)
        assert bot.main()

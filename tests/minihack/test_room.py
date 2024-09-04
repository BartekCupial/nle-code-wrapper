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
            "small_room",
            "small_room_random",
            "small_room_dark",
            "big_room",
            "big_room_random",
            "big_room_dark",
        ],
    )
    def test_solve_room_simple(self, env):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render"])
        bot = Bot(cfg)

        bot.global_strategy = partial(find_stairs, bot)
        assert bot.main()

    # @pytest.mark.parametrize(
    #     "env",
    #     [
    #         "small_room_monster",
    #         "small_room_trap",
    #         "small_room_ultimate",
    #         "big_room_monster",
    #         "big_room_trap",
    #         "big_room_ultimate",
    #     ],
    # )
    # def test_solve_room_hard(self, env):
    #     cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render"])
    #     bot = Bot(cfg)

    #     bot.global_strategy = partial(find_stairs, bot)
    #     assert bot.main()

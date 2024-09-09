import pytest

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.plugins.strategy import Strategy
from nle_code_wrapper.plugins.strategy.strategies import (
    explore,
    fight_closest_monster,
    goto_stairs,
    smart_fight_strategy,
)


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
    def test_solve_room_explore(self, env):
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

    @pytest.mark.parametrize(
        "env",
        [
            "small_room_monster",
            "big_room_monster",
        ],
    )
    @pytest.mark.parametrize("seed", [4])
    def test_solve_room_fight_easy(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        bot = Bot(cfg)

        @Strategy.wrap
        def general_fight(bot: "Bot"):
            fight_strat = fight_closest_monster(bot)
            stairs_strat = goto_stairs(bot)
            explore_strat = explore(bot)

            while True:
                try:
                    if fight_strat():
                        pass
                    elif stairs_strat():
                        pass
                    else:
                        explore_strat()
                except BotPanic:
                    pass
                yield True

        bot.strategy(general_fight)
        status = bot.main()
        assert status == bot.env.StepStatus.TASK_SUCCESSFUL

    @pytest.mark.parametrize(
        "env, seed",
        [
            ("small_room_trap", 17),
            ("big_room_trap", 2),
        ],
    )
    def test_solve_room_teleport_traps(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        bot = Bot(cfg)

        @Strategy.wrap
        def general_traps(bot: "Bot"):
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

        bot.strategy(general_traps)
        status = bot.main()
        assert status == bot.env.StepStatus.TASK_SUCCESSFUL

    @pytest.mark.parametrize(
        "env, seed",
        [
            ("big_room_monster", 33),
            ("big_room_ultimate", 4),
        ],
    )
    def test_solve_room_fight_hard(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        bot = Bot(cfg)

        @Strategy.wrap
        def general_smart_fight(bot: "Bot"):
            fight_strat = smart_fight_strategy(bot)
            stairs_strat = goto_stairs(bot)
            explore_strat = explore(bot)

            while True:
                try:
                    if fight_strat():
                        pass
                    elif stairs_strat():
                        pass
                    else:
                        explore_strat()
                except BotPanic:
                    pass
                yield True

        bot.strategy(general_smart_fight)
        status = bot.main()
        assert status == bot.env.StepStatus.TASK_SUCCESSFUL

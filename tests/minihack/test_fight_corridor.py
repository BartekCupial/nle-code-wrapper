import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategy import Strategy
from nle_code_wrapper.bot.strategy.strategies import explore, goto_stairs, smart_fight_strategy
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-CorridorBattle-v0",
            "MiniHack-CorridorBattle-Dark-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [2])
    def test_solve_room_fight_easy(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])

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

        cfg.strategies = [general_smart_fight]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

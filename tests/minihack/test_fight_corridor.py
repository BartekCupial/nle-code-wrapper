import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategy import Strategy
from nle_code_wrapper.bot.strategy.strategies import explore, fight_closest_monster, goto_stairs, run_away
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
    def test_solve_fight_corridor(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])

        @Strategy.wrap
        def general_smart_fight(bot: "Bot"):
            run_strat = run_away(bot)
            fight_strat = fight_closest_monster(bot)
            stairs_strat = goto_stairs(bot)
            explore_strat = explore(bot)

            while True:
                try:
                    if run_strat():
                        pass
                    elif fight_strat():
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

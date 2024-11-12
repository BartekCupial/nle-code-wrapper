import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategy import Strategy
from nle_code_wrapper.bot.strategy.strategies import explore, fight_closest_monster, goto_stairs, open_doors, run_away
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-MultiRoom-N2-Monster-v0",
            "MiniHack-MultiRoom-N4-Lava-v0",
            "MiniHack-MultiRoom-N6-v0",
            "MiniHack-MultiRoom-N6-Lava-v0",
            "MiniHack-MultiRoom-N6-LavaMonsters-v0",
            "MiniHack-MultiRoom-N6-Lava-OpenDoor-v0",
            "MiniHack-MultiRoom-N10-Lava-OpenDoor-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(3)))
    def test_solve_mazewalk(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render"])

        @Strategy.wrap
        def general(bot: "Bot"):
            run_strat = run_away(bot)
            fight_strat = fight_closest_monster(bot)
            stairs_strat = goto_stairs(bot)
            doors_strat = open_doors(bot)
            explore_strat = explore(bot)

            while True:
                try:
                    if run_strat():
                        pass
                    elif fight_strat():
                        pass
                    elif stairs_strat():
                        pass
                    elif doors_strat():
                        pass
                    else:
                        explore_strat()
                except BotPanic:
                    pass
                yield True

        cfg.strategies = [general]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

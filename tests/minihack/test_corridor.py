import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategy import Strategy
from nle_code_wrapper.bot.strategy.strategies import explore, goto_stairs, open_doors, open_doors_kick, search
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize("env", ["corridor3"])
    @pytest.mark.parametrize("seed", [0, 1])
    def test_corridor_open_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        status = play(cfg, strategies=[open_doors, goto_stairs, explore])
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize("env", ["corridor2"])
    @pytest.mark.parametrize("seed", [7])
    def test_corridor_closed_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])

        @Strategy.wrap
        def general_kick(bot: "Bot"):
            stairs_strat = goto_stairs(bot)
            door_strat = open_doors(bot)
            kick_strat = open_doors_kick(bot)
            explore_strat = explore(bot)

            while True:
                try:
                    if stairs_strat():
                        pass
                    elif door_strat():
                        kick_strat()
                    else:
                        explore_strat()
                except BotPanic:
                    pass
                yield True

        status = play(cfg, strategies=[general_kick])
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize("env", ["corridor3"])
    @pytest.mark.parametrize("seed", [9])
    def test_corridor_hidden_doors(self, env, seed):
        # TODO: add search
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])

        @Strategy.wrap
        def general_kick(bot: "Bot"):
            stairs_strat = goto_stairs(bot)
            door_strat = open_doors(bot)
            kick_strat = open_doors_kick(bot)
            explore_strat = explore(bot)
            search_strat = search(bot)

            while True:
                try:
                    if stairs_strat():
                        pass
                    elif door_strat():
                        kick_strat()
                    elif explore_strat():
                        pass
                    else:
                        search_strat()
                except BotPanic:
                    pass
                yield True

        status = play(cfg, strategies=[general_kick])
        assert status["end_status"].name == "TASK_SUCCESSFUL"

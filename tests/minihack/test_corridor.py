import pytest

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.play import play
from nle_code_wrapper.plugins.strategy import Strategy
from nle_code_wrapper.plugins.strategy.strategies import explore, goto_stairs, open_doors, open_doors_kick


def get_action(env, mode):
    return env.action_space.sample()


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize("env", ["corridor3"])
    @pytest.mark.parametrize("seed", [0, 1])
    def test_corridor_open_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        status = play(cfg, get_action=get_action, strategies=[open_doors, goto_stairs, explore])
        assert status == "TASK_SUCCESSFUL"

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

        status = play(cfg, get_action=get_action, strategies=[general_kick])
        assert status == "TASK_SUCCESSFUL"

    # @pytest.mark.parametrize("env", ["corridor3"])
    # @pytest.mark.parametrize("seed", [9])
    # def test_corridor_hidden_doors(self, env, seed):
    #     # TODO: add search
    #     cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
    #     bot = Bot(cfg)
    #     bot.strategy(open_door)
    #     bot.strategy(goto_stairs)
    #     bot.strategy(explore)
    # status = bot.main()
    # assert status == bot.env.StepStatus.TASK_SUCCESSFUL

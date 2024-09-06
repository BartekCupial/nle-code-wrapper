import pytest

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.strategies import explore, fight_all_monsters, goto_stairs, open_door


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize("env", ["corridor3"])
    @pytest.mark.parametrize("seed", [0, 1])
    def test_corridor_open_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        bot = Bot(cfg)
        bot.strategy(open_door)
        bot.strategy(fight_all_monsters)
        bot.strategy(goto_stairs)
        bot.strategy(explore)
        assert bot.main()

    @pytest.mark.parametrize("env", ["corridor2"])
    @pytest.mark.parametrize("seed", [7])
    def test_corridor_closed_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        bot = Bot(cfg)
        bot.strategy(open_door)
        bot.strategy(fight_all_monsters)
        bot.strategy(goto_stairs)
        bot.strategy(explore)
        assert bot.main()

    # @pytest.mark.parametrize("env", ["corridor3"])
    # @pytest.mark.parametrize("seed", [9])
    # def test_corridor_hidden_doors(self, env, seed):
    #     # TODO: add search
    #     cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
    #     bot = Bot(cfg)
    #     bot.strategy(open_door)
    #     bot.strategy(fight_all_monsters)
    #     bot.strategy(goto_stairs)
    #     bot.strategy(explore)
    #     assert bot.main()

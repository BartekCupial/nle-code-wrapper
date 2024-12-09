import pytest

from nle_code_wrapper.bot.exceptions import BotFinished
from nle_code_wrapper.bot.strategies import explore_corridor, open_doors
from nle_code_wrapper.bot.strategies.cross_lava_river import levitate, levitate_over_lava_river
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestCrossLavaRive:
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-LavaCross-Levitate-Potion-Inv-Full-v0",
            "MiniHack-LavaCross-Levitate-Ring-Inv-Full-v0",
            "MiniHack-LavaCross-Levitate-Potion-Pickup-Full-v0",
            "MiniHack-LavaCross-Levitate-Ring-Pickup-Full-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_lavacross(self, env, seed):
        """
        This tests checks if we were able to pick cross lava river
        """
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        assert levitate_over_lava_river(bot)

    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-Levitate-Boots-Full-v0",
            "MiniHack-Levitate-Ring-Full-v0",
            "MiniHack-Levitate-Potion-Full-v0",
            "MiniHack-Levitate-Random-Full-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_levitate(self, env, seed):
        """
        This test checks if we were able to make ourselves levitate
        """
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        with pytest.raises(BotFinished):
            levitate(bot)

    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-Quest-Hard-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0, 2])
    def test_quest_hard(self, env, seed):
        """
        This test checks if we can levitate over the river in quest hard
        """
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        explore_corridor(bot)
        open_doors(bot)
        open_doors(bot)
        assert levitate_over_lava_river(bot)

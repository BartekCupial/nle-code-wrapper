import pytest

from nle_code_wrapper.bot.exceptions import BotFinished
from nle_code_wrapper.bot.strategies import (
    acquire_levitation,
    explore_corridor,
    freeze_lava_river,
    goto_closest_corridor,
    levitate_over_lava_river,
    open_doors,
)
from nle_code_wrapper.envs.custom.play_custom import parse_custom_args
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

        try:
            assert levitate_over_lava_river(bot)
        except BotFinished:
            pass

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
            acquire_levitation(bot)

    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-Quest-Hard-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0, 2])
    def test_quest_hard_levitate(self, env, seed):
        """
        This test checks if we can levitate over the river in quest hard
        """
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        explore_corridor(bot)
        open_doors(bot)
        open_doors(bot)
        assert levitate_over_lava_river(bot)

    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-Quest-Hard-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [1, 3, 4])
    def test_quest_hard_freeze(self, env, seed):
        """
        This test checks if we can freeze the river in quest hard
        """
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        explore_corridor(bot)
        open_doors(bot)
        open_doors(bot)
        assert freeze_lava_river(bot)

    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-MonsterlessQuest-Medium-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(5)))
    def test_quest_medium_freeze(self, env, seed):
        """
        This test checks if we can freeze the river in quest medium
        """
        cfg = parse_custom_args(
            argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False", "--autopickup=True"]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        goto_closest_corridor(bot)
        explore_corridor(bot)
        try:
            assert freeze_lava_river(bot)
        except BotFinished:
            pass

    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-MonsterlessQuest-Easy-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(5)))
    def test_quest_easy_freeze(self, env, seed):
        """
        This test checks if we can freeze the river in quest easy
        """
        cfg = parse_custom_args(
            argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False", "--autopickup=True"]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        try:
            assert freeze_lava_river(bot)
        except BotFinished:
            pass

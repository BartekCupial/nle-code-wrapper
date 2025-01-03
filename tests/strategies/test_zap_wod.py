import pytest

from nle_code_wrapper.bot.exceptions import BotFinished
from nle_code_wrapper.bot.strategies.explore import explore_room
from nle_code_wrapper.bot.strategies.pickup import pickup_wand
from nle_code_wrapper.bot.strategies.run_away import run_away
from nle_code_wrapper.bot.strategies.zap_monster import approach_and_zap_monster
from nle_code_wrapper.envs.custom.play_custom import parse_custom_args
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestZapWoD:
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-WoD-Easy-Full-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_wod_easy(self, env, seed):
        """
        This tests checks if we were able to zap WoD to kill monster
        """
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        try:
            approach_and_zap_monster(bot)
        except BotFinished:
            pass
        assert bot.reward > 0

    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-WoD-Medium-Full-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_wod_medium(self, env, seed):
        """
        This tests checks if we were able to zap WoD to kill monster
        """
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_wand(bot)
        approach_and_zap_monster(bot)

        assert "You kill the minotaur!" in bot.message or "The death ray misses the minotaur." in bot.message

    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-WoD-Hard-Full-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_wod_hard(self, env, seed):
        """
        This tests checks if we were able to zap WoD to kill monster
        """
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_wand(bot)
        explore_room(bot)
        approach_and_zap_monster(bot)

        assert "You kill the minotaur!" in bot.message or "The death ray misses the minotaur." in bot.message

    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-WoD-Melee-Full-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_wod_melee(self, env, seed):
        """
        This tests checks if we were able to zap WoD to kill monster
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        approach_and_zap_monster(bot)
        run_away(bot)

        try:
            approach_and_zap_monster(bot)
        except BotFinished:
            pass
        assert bot.reward > 0

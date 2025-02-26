import pytest

from nle_code_wrapper.bot.exceptions import BotFinished
from nle_code_wrapper.bot.strategies import loot_container, open_container_key, open_container_kick, pickup_tool
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestContainer:
    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-Chest-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [2])
    def test_container_unlocked(self, env, seed):
        """
        This tests checks if we were able to pick cross lava river
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        try:
            assert loot_container(bot)
        except BotFinished:
            pass

    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-Chest-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [1])
    def test_container_locked_key(self, env, seed):
        """
        This tests checks if we were able to pick cross lava river
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_tool(bot)
        open_container_key(bot)
        try:
            assert loot_container(bot)
        except BotFinished:
            pass

    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-Chest-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [1])
    def test_container_locked_kick(self, env, seed):
        """
        This tests checks if we were able to pick cross lava river
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        open_container_kick(bot)
        try:
            assert loot_container(bot)
        except BotFinished:
            pass

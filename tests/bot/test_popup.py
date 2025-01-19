import pytest
from nle.nethack import actions as A

from nle_code_wrapper.bot.strategies import goto_item, pickup_armor
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestRaySimulator:
    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-WearSuit-Pile-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_popup_inventory(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        bot.type_text("i")
        popup_message = bot.message
        bot.type_text(" ")

        assert len(popup_message.split("\n")) > 2

    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-WearSuit-SmallPile-v0"),
            ("CustomMiniHack-WearSuit-Pile-v0"),
            ("CustomMiniHack-WearSuit-HugePile-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_popup_pickup(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        goto_item(bot)
        bot.step(A.Command.PICKUP)
        popup_message = bot.message

        assert len(popup_message.split("\n")) > 2

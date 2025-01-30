import pytest

from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestEat:
    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-Corpse-v0",
        ],
    )
    def test_parse_character(self, env):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--character=@",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        for i in range(1000):
            bot.reset(seed=i)
            str(bot.character)

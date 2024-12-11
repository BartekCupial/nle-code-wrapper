import pytest

from nle_code_wrapper.bot.exceptions import BotFinished
from nle_code_wrapper.bot.strategies.explore import explore_room, explore_room_systematically
from nle_code_wrapper.bot.strategies.fight_monster import zap_monster_wand
from nle_code_wrapper.bot.strategies.push_boulder import goto_boulder, push_boulder_direction, push_boulder_into_river
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestRiver:
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-River-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_push_boulder(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        explore_room_systematically(bot)
        goto_boulder(bot)
        push_boulder_direction(bot, "west")
        push_boulder_direction(bot, "north")
        assert "With great effort you move the boulder" in bot.message

    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-River-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_push_boulder_into_river(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        explore_room_systematically(bot)
        goto_boulder(bot)
        push_boulder_into_river(bot)
        assert "You push the boulder into the water." in bot.message

import pytest

from nle_code_wrapper.bot.strategies.explore import explore_room, explore_room_systematically
from nle_code_wrapper.bot.strategies.push_boulder import (
    align_boulder_for_bridge,
    goto_boulder,
    goto_boulder_closest_to_river,
    push_boulder_direction,
    push_boulder_into_river,
)
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

        explore_room(bot)
        goto_boulder_closest_to_river(bot)
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

        explore_room(bot)
        goto_boulder_closest_to_river(bot)
        push_boulder_into_river(bot)
        assert "It sinks without a trace!" in bot.message or "You push the boulder into the water." in bot.message

    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-River-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_goto_boulder_closest_to_river(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        explore_room(bot)
        goto_boulder_closest_to_river(bot)
        push_boulder_direction(bot, "north")
        assert "With great effort you move the boulder" in bot.message

    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-River-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [3])
    def test_align_boulder_for_bridge(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        # push the first boulder
        explore_room(bot)
        goto_boulder_closest_to_river(bot)
        push_boulder_into_river(bot)

        # align and push the second boulder
        explore_room(bot)
        goto_boulder_closest_to_river(bot)
        align_boulder_for_bridge(bot)
        push_boulder_into_river(bot)

        assert "It sinks without a trace!" in bot.message or "You push the boulder into the water." in bot.message

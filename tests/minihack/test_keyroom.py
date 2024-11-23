import pytest
from nle.nethack import actions as A
from nle_utils.glyph import G
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import (
    explore_corridor_systematically,
    explore_room,
    goto_closest_staircase_down,
    goto_closest_unexplored_corridor,
    goto_closest_unexplored_room,
    open_doors_key,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils import utils


def position_of_closest_object(bot, obj):
    coords = utils.coords(bot.glyphs, obj)
    distances = bot.pathfinder.distances(bot.entity.position)

    position = min(
        (e for e in coords if e in distances),
        key=lambda e: distances[e],
        default=None,
    )

    return position


def position_of_reachable_adjacent_object(bot: "Bot", obj):
    coords = utils.coords(bot.glyphs, obj)

    reachable = min(
        (e for e in coords if bot.pathfinder.reachable_adjacent(bot.entity.position, e)),
        key=lambda e: bot.pathfinder.distance(bot.entity.position, e),
        default=None,
    )

    return reachable


def pickup_key(bot: "Bot"):
    position = position_of_closest_object(bot, G.TOOL_CLASS)

    if position:
        bot.pathfinder.goto(position)
        bot.step(A.Command.PICKUP)
        return True
    else:
        return False


def solve(bot: "Bot"):
    has_key = False
    while True:
        try:
            closed_doors = position_of_reachable_adjacent_object(bot, G.DOOR_CLOSED)

            if goto_closest_staircase_down(bot):
                pass
            elif has_key and closed_doors:
                open_doors_key(bot)
            elif pickup_key(bot):
                has_key = True
            elif explore_room(bot):
                pass
            elif explore_corridor_systematically(bot):
                pass
            elif goto_closest_unexplored_room(bot):
                pass
            else:
                goto_closest_unexplored_corridor(bot)

        except BotPanic:
            pass


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env, seed",
        [
            ("MiniHack-KeyRoom-Fixed-S5-v0", 7),
            ("MiniHack-KeyRoom-S5-v0", 7),
            ("MiniHack-KeyRoom-Dark-S5-v0", 7),
            ("MiniHack-KeyRoom-S15-v0", 7),
            ("MiniHack-KeyRoom-Dark-S15-v0", 7),
        ],
    )
    def test_keyroom_hard(self, env, seed):
        # TODO: this is quite weak strategy for general exploration of the levels
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        cfg.strategies = [solve]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

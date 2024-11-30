import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import (
    explore_corridor_systematically,
    explore_room,
    fight_closest_monster,
    goto_closest_room,
    goto_closest_staircase_down,
    run_away,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


def multiple_monsters_adjacent(bot: "Bot") -> bool:
    return len([e for e in bot.entities if bot.pathfinder.distance(e.position, bot.entity.position) == 1]) > 1


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-CorridorBattle-v0",
            "MiniHack-CorridorBattle-Dark-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [2])
    def test_solve_fight_corridor(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])

        def solve(bot: "Bot"):
            while True:
                try:
                    if multiple_monsters_adjacent(bot):
                        if run_away(bot):
                            pass
                    elif fight_closest_monster(bot):
                        pass
                    elif goto_closest_staircase_down(bot):
                        pass
                    elif explore_room(bot):
                        pass
                    elif explore_corridor_systematically(bot):
                        pass
                    else:
                        goto_closest_room(bot)

                except BotPanic:
                    pass

        cfg.strategies = [solve]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

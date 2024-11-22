import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import (
    explore_corridor,
    explore_room,
    goto_closest_staircase_down,
    goto_closest_unexplored_room,
    open_doors_kick,
    search_corridor_for_hidden_doors,
    search_room_for_hidden_doors,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize("env", ["MiniHack-Corridor-R2-v0", "MiniHack-Corridor-R3-v0", "MiniHack-Corridor-R5-v0"])
    @pytest.mark.parametrize("seed", list(range(10)))
    def test_corridor_open_doors(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])

        def general_solve(bot: "Bot"):
            while True:
                for strategy in [
                    goto_closest_staircase_down,
                    explore_room,
                    explore_corridor,
                    open_doors_kick,
                    goto_closest_unexplored_room,
                    search_corridor_for_hidden_doors,
                    search_room_for_hidden_doors,
                ]:
                    try:
                        if strategy(bot):
                            break
                    except BotPanic:
                        pass

        cfg.strategies = [general_solve]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

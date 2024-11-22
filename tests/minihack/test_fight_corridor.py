import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import (
    fight_closest_monster,
    general_explore,
    goto_closest_staircase_down,
    run_away,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


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

        def general_smart_fight(bot: "Bot"):
            while True:
                try:
                    if run_away(bot):
                        pass
                    elif fight_closest_monster(bot):
                        pass
                    elif goto_closest_staircase_down(bot):
                        pass
                    else:
                        general_explore(bot)
                except BotPanic:
                    pass

        cfg.strategies = [general_smart_fight]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

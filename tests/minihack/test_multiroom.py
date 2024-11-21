import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import fight_closest_monster, general_explore, goto_stairs, open_doors, run_away
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-MultiRoom-N2-Monster-v0",
            "MiniHack-MultiRoom-N4-Lava-v0",
            "MiniHack-MultiRoom-N6-v0",
            "MiniHack-MultiRoom-N6-Lava-v0",
            "MiniHack-MultiRoom-N6-LavaMonsters-v0",
            "MiniHack-MultiRoom-N6-Lava-OpenDoor-v0",
            "MiniHack-MultiRoom-N10-Lava-OpenDoor-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(3)))
    def test_solve_multiroom(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render"])

        def general(bot: "Bot"):
            while True:
                try:
                    if run_away(bot):
                        pass
                    elif fight_closest_monster(bot):
                        pass
                    elif goto_stairs(bot):
                        pass
                    elif open_doors(bot):
                        pass
                    else:
                        general_explore(bot)
                except BotPanic:
                    pass

        cfg.strategies = [general]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

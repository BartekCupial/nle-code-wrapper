import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import (
    explore_room,
    fight_monster,
    fight_multiple_monsters,
    goto_downstairs,
    goto_unexplored_corridor,
    goto_unexplored_room,
    open_doors,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-MultiRoom-N2-Monster-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(3)))
    def test_solve_multiroom_monster(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
            ]
        )

        def solve(bot: "Bot"):
            while True:
                try:
                    if fight_multiple_monsters(bot):
                        pass
                    elif fight_monster(bot):
                        pass
                    elif goto_downstairs(bot):
                        pass
                    elif open_doors(bot):
                        pass
                    elif explore_room(bot):
                        pass
                    elif goto_unexplored_corridor(bot):
                        pass
                    else:
                        goto_unexplored_room(bot)

                except BotPanic:
                    pass

        cfg.strategies = [solve]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize(
        "env",
        [
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
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
            ]
        )

        def general_solve(bot: "Bot"):
            while True:
                for strategy in [
                    fight_multiple_monsters,
                    fight_monster,
                    goto_downstairs,
                    open_doors,
                    goto_unexplored_corridor,
                    explore_room,
                    goto_unexplored_room,
                ]:
                    try:
                        strategy(bot)
                    except BotPanic:
                        pass

        cfg.strategies = [general_solve]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

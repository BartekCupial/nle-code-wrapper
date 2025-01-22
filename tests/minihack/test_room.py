import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import explore_room, fight_monster, goto_downstairs, run_away
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-Room-5x5-v0",
            "MiniHack-Room-Random-5x5-v0",
            "MiniHack-Room-Dark-5x5-v0",
            "MiniHack-Room-15x15-v0",
            "MiniHack-Room-Random-15x15-v0",
            "MiniHack-Room-Dark-15x15-v0",
        ],
    )
    def test_solve_room_explore(self, env):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
            ]
        )

        def solve(bot: "Bot"):
            while True:
                try:
                    if goto_downstairs(bot):
                        pass
                    else:
                        explore_room(bot)
                except BotPanic:
                    pass

        cfg.strategies = [solve]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-Room-Monster-5x5-v0",
            "MiniHack-Room-Monster-15x15-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [4])
    def test_solve_room_fight_easy(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )

        def general_fight(bot: "Bot"):
            while True:
                try:
                    if fight_monster(bot):
                        pass
                    elif goto_downstairs(bot):
                        pass
                    else:
                        explore_room(bot)
                except BotPanic:
                    pass

        cfg.strategies = [general_fight]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize(
        "env, seed",
        [
            ("MiniHack-Room-Trap-5x5-v0", 17),
            ("MiniHack-Room-Trap-15x15-v0", 2),
        ],
    )
    def test_solve_room_teleport_traps(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )

        def general_traps(bot: "Bot"):
            while True:
                try:
                    if goto_downstairs(bot):
                        pass
                    else:
                        explore_room(bot)
                except BotPanic:
                    pass

        cfg.strategies = [general_traps]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize(
        "env, seed",
        [
            ("MiniHack-Room-Monster-15x15-v0", 33),
            ("MiniHack-Room-Ultimate-15x15-v0", 4),
        ],
    )
    def test_solve_room_fight_hard(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )

        def general_smart_fight(bot: "Bot"):
            while True:
                try:
                    if fight_monster(bot):
                        pass
                    elif goto_downstairs(bot):
                        pass
                    else:
                        explore_room(bot)
                except BotPanic:
                    pass

        cfg.strategies = [general_smart_fight]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

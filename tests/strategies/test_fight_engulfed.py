import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotFinished, BotPanic
from nle_code_wrapper.bot.strategies import (
    explore_corridor,
    explore_room,
    fight_engulfed,
    fight_multiple_monsters,
    goto_corridor,
    goto_downstairs,
    goto_room,
    goto_unexplored_room,
    open_doors,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestFightEngulfed:
    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-FightEngulfed-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(3)))
    def test_fight_multiple_monsters(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )

        def solve(bot: "Bot"):
            goto_corridor(bot)
            while True:
                try:
                    if fight_multiple_monsters(bot):
                        continue
                    elif fight_engulfed(bot):
                        continue
                    elif goto_downstairs(bot):
                        continue
                    else:
                        goto_room(bot)
                except BotPanic:
                    pass

        cfg.strategies = [solve]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

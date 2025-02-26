import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotFinished, BotPanic
from nle_code_wrapper.bot.strategies import (
    descend_stairs,
    explore_corridor,
    explore_room,
    fight_engulfed,
    fight_melee,
    goto_corridor,
    goto_room,
    goto_unexplored_room,
    open_doors,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestFightNeutral:
    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-FightNeutral-v0",
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
            fight_melee(bot)
            bot.type_text("y")
            fight_melee(bot)
            descend_stairs(bot)

        cfg.strategies = [solve]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

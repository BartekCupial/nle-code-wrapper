import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotFinished, BotPanic
from nle_code_wrapper.bot.strategies import (
    descend_stairs,
    examine_items,
    explore_corridor,
    explore_room,
    fight_multiple_monsters,
    fight_ranged,
    goto_corridor,
    goto_room,
    goto_unexplored_room,
    open_doors,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestFightRanged:
    @pytest.mark.parametrize(
        "env",
        [
            "CustomMiniHack-FightRanged-v0",
        ],
    )
    @pytest.mark.parametrize("seed", list(range(3)))
    def test_fight_ranged(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--autopickup=True",
                "--code_wrapper=False",
            ]
        )

        bot = create_bot(cfg)
        bot.reset(seed=seed)

        examine_items(bot)
        goto_corridor(bot)
        while fight_ranged(bot):
            pass
        with pytest.raises(BotFinished):
            descend_stairs(bot)

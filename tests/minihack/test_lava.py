from functools import partial

import pytest
from nle import nethack
from nle.nethack import actions as A
from nle_utils.glyph import G
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategies import goto_stairs, quaff_potion_from_inv
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils import utils


def lava_strategy(bot: "Bot"):
    while True:
        goto(bot, G.RING_CLASS)
        goto(bot, G.POTION_CLASS)
        pickup(bot)
        if quaff_potion_from_inv(bot):
            pass
        else:
            put_on_ring_from_inv(bot)
        goto_stairs(bot)


def pickup(bot: "Bot"):
    bot.step(A.Command.PICKUP)

    if bot.message.strip() == "":
        return False
    else:
        return True


def goto(bot: "Bot", where):
    coords = utils.coords(bot.glyphs, where)
    distances = bot.pathfinder.distances(bot.entity.position)

    position = min(
        (e for e in coords if e in distances),
        key=lambda e: distances[e],
        default=None,
    )

    if position:
        bot.pathfinder.goto(position)
        return True
    else:
        return False


def put_on_ring_from_inv(bot: "Bot"):
    inv_letters = bot.inv_letters
    inv_oclasses = bot.inv_oclasses

    ring_letters = inv_letters[inv_oclasses == nethack.RING_CLASS]

    # find the ring of levitation
    levitation = False
    for ring_char in ring_letters:
        bot.step(A.Command.PUTON)
        bot.step(ring_char)
        bot.type_text("l")  # indicates left ring finger - not sure if this matters

        if bot.blstats.prop_mask & nethack.BL_MASK_LEV:
            levitation = True
            break
        else:
            bot.step(A.Command.REMOVE)

    return levitation


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env",
        [
            "MiniHack-LavaCross-Levitate-Potion-Inv-Full-v0",
            "MiniHack-LavaCross-Levitate-Ring-Inv-Full-v0",
            "MiniHack-LavaCross-Levitate-Potion-Pickup-Full-v0",
            "MiniHack-LavaCross-Levitate-Ring-Pickup-Full-v0",
        ],
    )
    @pytest.mark.parametrize("seed", [0, 1, 2, 3, 4])
    def test_lava(self, env, seed):
        # TODO: for some of the variants there are monsters which have to be dealt with
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        cfg.strategies = [lava_strategy]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

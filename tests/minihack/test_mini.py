from functools import partial
from typing import Callable

import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import (
    descend_stairs,
    eat_food_inventory,
    explore_room,
    fight_melee,
    goto_unexplored_corridor,
    goto_unexplored_room,
    open_doors_kick,
    pickup_amulet,
    pickup_armor,
    pickup_food,
    pickup_scroll,
    pickup_wand,
    pickup_weapon,
    pray_altar,
    puton_amulet,
    quaff_sink,
    read_scroll,
    wear_cloak,
    wield_melee_weapon,
    zap_wand,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


def general_mini(bot: "Bot", action: Callable):
    while True:
        fight_melee(bot)
        explore_room(bot)
        action(bot)


def pickup_and_act(bot, pickup, act):
    pickup(bot)
    act(bot)


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize("env", ["MiniHack-LockedDoor-Fixed-v0"])
    @pytest.mark.parametrize("seed", list(range(5)))
    def test_mini_locked(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )

        def solve(bot: "Bot"):
            while True:
                try:
                    open_doors_kick(bot)
                    explore_room(bot)
                    descend_stairs(bot)
                except BotPanic:
                    pass

        cfg.strategies = [solve]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize("env", ["MiniHack-LockedDoor-v0"])
    @pytest.mark.parametrize("seed", list(range(5)))
    def test_mini_locked_dynamic(self, env, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )

        def solve(bot: "Bot"):
            while True:
                try:
                    open_doors_kick(bot)
                    explore_room(bot)
                    goto_unexplored_corridor(bot)
                    goto_unexplored_room(bot)
                    descend_stairs(bot)
                except BotPanic:
                    pass

        cfg.strategies = [solve]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize(
        "env, action",
        [
            ("MiniHack-Eat-v0", partial(pickup_and_act, pickup=pickup_food, act=eat_food_inventory)),
            ("MiniHack-Read-v0", partial(pickup_and_act, pickup=pickup_scroll, act=read_scroll)),
            ("MiniHack-Zap-v0", partial(pickup_and_act, pickup=pickup_wand, act=zap_wand)),
            ("MiniHack-PutOn-v0", partial(pickup_and_act, pickup=pickup_amulet, act=puton_amulet)),
            ("MiniHack-Wear-v0", partial(pickup_and_act, pickup=pickup_armor, act=wear_cloak)),
            # doesn't work because we wield best weapon and here dagger is worse
            # ("MiniHack-Wield-v0", partial(pickup_and_act, pickup=pickup_weapon, act=wield_melee_weapon)),
            ("MiniHack-Eat-Distr-v0", partial(pickup_and_act, pickup=pickup_food, act=eat_food_inventory)),
            ("MiniHack-Read-Distr-v0", partial(pickup_and_act, pickup=pickup_scroll, act=read_scroll)),
            ("MiniHack-Zap-Distr-v0", partial(pickup_and_act, pickup=pickup_wand, act=zap_wand)),
            ("MiniHack-PutOn-Distr-v0", partial(pickup_and_act, pickup=pickup_amulet, act=puton_amulet)),
            ("MiniHack-Wear-Distr-v0", partial(pickup_and_act, pickup=pickup_armor, act=wear_cloak)),
            # doesn't work because we wield best weapon and here dagger is worse
            # ("MiniHack-Wield-Distr-v0", partial(pickup_and_act, pickup=pickup_weapon, act=wield_melee_weapon)),
        ],
    )
    @pytest.mark.parametrize("seed", list(range(5)))
    def test_mini(self, env, action, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )
        cfg.strategies = [partial(general_mini, action=action)]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize(
        "env, action",
        [
            ("MiniHack-Pray-v0", pray_altar),
            ("MiniHack-Sink-v0", quaff_sink),
            ("MiniHack-Pray-Distr-v0", pray_altar),
            ("MiniHack-Sink-Distr-v0", quaff_sink),
        ],
    )
    @pytest.mark.parametrize("seed", list(range(5)))
    def test_mini_special(self, env, action, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )
        cfg.strategies = [partial(general_mini, action=action)]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

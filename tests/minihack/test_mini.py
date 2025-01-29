from functools import partial

import numpy as np
import pytest
from nle.nethack import actions as A
from nle_utils.glyph import G
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.bot.strategies import (
    descend_stairs,
    explore_room,
    fight_monster,
    goto_unexplored_corridor,
    goto_unexplored_room,
    open_doors_kick,
    random_move,
)
from nle_code_wrapper.bot.strategies.goto import goto_closest
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils import utils


def general_mini(bot: "Bot", where, action):
    while True:
        fight_monster(bot)
        explore_room(bot)
        goto(bot, where, action)


command_item_map = {
    A.Command.EAT: G.FOOD_OBJECTS,
    A.Command.PRAY: G.ALTAR,
    A.Command.QUAFF: frozenset.union(G.SINK, G.POTION_CLASS),
    A.Command.READ: G.SCROLL_CLASS,
    A.Command.ZAP: G.WAND_CLASS,
    A.Command.PUTON: frozenset.union(G.AMULET_CLASS, G.RING_CLASS),
    A.Command.WEAR: G.ARMOR_CLASS,
    A.Command.WIELD: G.WEAPON_CLASS,
}


def goto(bot: "Bot", where, action):
    positions = np.argwhere(utils.isin(bot.glyphs, where))
    if goto_closest(bot, positions):
        return action(bot)
    else:
        positions = np.argwhere(utils.isin(bot.glyphs, G.ITEMS))
        if goto_closest(bot, positions):
            return action(bot)
        else:
            random_move(bot)
            return False


def try_current_items(bot, command):
    item_class = command_item_map[command]

    # find item in the inventory
    item_char = None
    for item in bot.inventory.items:
        if item.glyph in item_class:
            item_char = item.letter

            bot.step(command)
            bot.step(item_char)

            # if the game isn't finished, remove item
            bot.step(A.Command.TAKEOFFALL)

    return False


def make_action_and_confirm(bot, command):
    bot.step(command)
    bot.type_text("y")


def pickup_and_use_item(bot, command):
    try_current_items(bot, command)

    bot.step(A.Command.PICKUP)
    if bot.message:
        letter = bot.message[0]
        bot.step(command)
        bot.type_text(letter)

        if "Which ring-finger, Right or Left?" in bot.message:
            bot.type_text("r")
    else:
        # there is a bug in the env, we cannot pick sth up and we should have
        pass


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
        "env, where, action",
        [
            ("MiniHack-Eat-v0", G.FOOD_OBJECTS, partial(make_action_and_confirm, command=A.Command.EAT)),
            ("MiniHack-Pray-v0", G.ALTAR, partial(make_action_and_confirm, command=A.Command.PRAY)),
            ("MiniHack-Sink-v0", G.SINK, partial(make_action_and_confirm, command=A.Command.QUAFF)),
            ("MiniHack-Read-v0", G.SCROLL_CLASS, partial(pickup_and_use_item, command=A.Command.READ)),
            ("MiniHack-Zap-v0", G.WAND_CLASS, partial(pickup_and_use_item, command=A.Command.ZAP)),
            (
                "MiniHack-PutOn-v0",
                frozenset.union(G.AMULET_CLASS, G.RING_CLASS),
                partial(pickup_and_use_item, command=A.Command.PUTON),
            ),
            ("MiniHack-Wear-v0", G.ARMOR_CLASS, partial(pickup_and_use_item, command=A.Command.WEAR)),
            ("MiniHack-Wield-v0", G.WEAPON_CLASS, partial(pickup_and_use_item, command=A.Command.WIELD)),
        ],
    )
    @pytest.mark.parametrize("seed", list(range(5)))
    def test_mini(self, env, where, action, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )
        cfg.strategies = [partial(general_mini, where=where, action=action)]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize(
        "env, where, action",
        [
            ("MiniHack-Eat-Distr-v0", G.FOOD_OBJECTS, partial(make_action_and_confirm, command=A.Command.EAT)),
            ("MiniHack-Pray-Distr-v0", G.ALTAR, partial(make_action_and_confirm, command=A.Command.PRAY)),
            ("MiniHack-Sink-Distr-v0", G.SINK, partial(make_action_and_confirm, command=A.Command.QUAFF)),
            ("MiniHack-Read-Distr-v0", G.SCROLL_CLASS, partial(pickup_and_use_item, command=A.Command.READ)),
            ("MiniHack-Zap-Distr-v0", G.WAND_CLASS, partial(pickup_and_use_item, command=A.Command.ZAP)),
            (
                "MiniHack-PutOn-Distr-v0",
                frozenset.union(G.AMULET_CLASS, G.RING_CLASS),
                partial(pickup_and_use_item, command=A.Command.PUTON),
            ),
            ("MiniHack-Wear-Distr-v0", G.ARMOR_CLASS, partial(pickup_and_use_item, command=A.Command.WEAR)),
            ("MiniHack-Wield-Distr-v0", G.WEAPON_CLASS, partial(pickup_and_use_item, command=A.Command.WIELD)),
        ],
    )
    @pytest.mark.parametrize("seed", list(range(1)))
    def test_mini_distract(self, env, where, action, seed):
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                "--no-render",
                f"--seed={seed}",
            ]
        )
        cfg.strategies = [partial(general_mini, where=where, action=action)]
        status = play(cfg, get_action=lambda *_: 0)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

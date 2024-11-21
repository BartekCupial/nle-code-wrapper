from functools import partial

import pytest
from nle.nethack import actions as A
from nle_utils.glyph import G
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategies import (
    fight_all_monsters,
    general_explore,
    goto_stairs,
    open_doors_kick,
    random_move,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils import utils


def general_mini(bot: "Bot", where, action):
    while True:
        fight_all_monsters(bot)
        general_explore(bot)
        goto(bot, where, action)


def goto(bot: "Bot", where, action):
    coords = utils.coords(bot.glyphs, where)
    distances = bot.pathfinder.distances(bot.entity.position)

    position = min(
        (e for e in coords if e in distances),
        key=lambda e: distances[e],
        default=None,
    )

    if position:
        bot.pathfinder.goto(position)
        action(bot)
        return True
    else:
        random_move(bot)
        return False


def make_action_and_confirm(bot, command):
    bot.step(command)
    bot.type_text("y")


def pickup_and_use_item(bot, command):
    bot.step(A.Command.PICKUP)
    letter = bot.message[0]
    bot.step(command)
    bot.type_text(letter)


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env, where, action",
        [
            ("MiniHack-Eat-Fixed-v0", G.FOOD_OBJECTS, partial(make_action_and_confirm, command=A.Command.EAT)),
            ("MiniHack-Pray-Fixed-v0", G.ALTAR, partial(make_action_and_confirm, command=A.Command.PRAY)),
            ("MiniHack-Sink-Fixed-v0", G.SINK, partial(make_action_and_confirm, command=A.Command.QUAFF)),
            ("MiniHack-Read-Fixed-v0", G.SCROLL_CLASS, partial(pickup_and_use_item, command=A.Command.READ)),
            ("MiniHack-Zap-Fixed-v0", G.WAND_CLASS, partial(pickup_and_use_item, command=A.Command.ZAP)),
            (
                "MiniHack-PutOn-Fixed-v0",
                frozenset.union(G.AMULET_CLASS, G.RING_CLASS),
                partial(pickup_and_use_item, command=A.Command.PUTON),
            ),
            ("MiniHack-Wear-Fixed-v0", G.ARMOR_CLASS, partial(pickup_and_use_item, command=A.Command.WEAR)),
            ("MiniHack-Wield-Fixed-v0", G.WEAPON_CLASS, partial(pickup_and_use_item, command=A.Command.WIELD)),
        ],
    )
    @pytest.mark.parametrize("seed", [1])
    def test_mini_fixed(self, env, where, action, seed):
        # TODO: for some of the variants there are monsters which have to be dealt with
        # TODO: for some of the seeds there are items already worn, which have to be taken off
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        cfg.strategies = [partial(general_mini, where=where, action=action)]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize("env", ["MiniHack-LockedDoor-Fixed-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_mini_locked(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        bot = Bot(cfg)

        bot.strategy(open_doors_kick)
        bot.strategy(general_explore)
        bot.strategy(goto_stairs)

        cfg.strategies = [open_doors_kick, general_explore, goto_stairs]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

    @pytest.mark.parametrize("env", ["MiniHack-LockedDoor-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_mini_locked_dynamic(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        bot = Bot(cfg)

        bot.strategy(open_doors_kick)
        bot.strategy(general_explore)
        bot.strategy(goto_stairs)

        cfg.strategies = [open_doors_kick, general_explore, goto_stairs]
        status = play(cfg)
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
    @pytest.mark.parametrize("seed", [100])
    def test_mini_dynamic(self, env, where, action, seed):
        # TODO: for some of the variants there are monsters which have to be dealt with
        # TODO: for some of the seeds there are items already worn, which have to be taken off
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        cfg.strategies = [partial(general_mini, where=where, action=action)]
        status = play(cfg)
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
    @pytest.mark.parametrize("seed", [100])
    def test_mini_distract(self, env, where, action, seed):
        # TODO: for some of the variants there are monsters which have to be dealt with
        # TODO: for some of the seeds there are items already worn, which have to be taken off
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        cfg.strategies = [partial(general_mini, where=where, action=action)]
        status = play(cfg)
        assert status["end_status"].name == "TASK_SUCCESSFUL"

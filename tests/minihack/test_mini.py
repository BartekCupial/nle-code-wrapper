from functools import partial

import pytest
from nle.nethack import actions as A
from nle_utils.glyph import G

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.plugins.strategy import Strategy
from nle_code_wrapper.plugins.strategy.strategies import (
    explore,
    fight_all_monsters,
    goto_stairs,
    open_doors_kick,
    random_move,
)
from nle_code_wrapper.utils import utils


@Strategy.wrap
def general_mini(bot: "Bot", where, action):
    fight_strat = fight_all_monsters(bot)
    explore_strat = explore(bot)
    goto_strat = goto(bot, where, action)

    while True:
        fight_strat()
        explore_strat()
        goto_strat()
        yield


@Strategy.wrap
def goto(bot: "Bot", where, action):
    random_strat = random_move(bot)

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
        yield True
    else:
        random_strat()
        yield False


def make_action_and_confirm(bot, command):
    bot.step(command)
    bot.type_text("y")


def pickup_and_use_item(bot, command):
    bot.pickup()
    letter = bot.message[0]
    bot.step(command)
    bot.type_text(letter)


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env, where, action",
        [
            ("mini_eat_fixed", G.FOOD_OBJECTS, partial(make_action_and_confirm, command=A.Command.EAT)),
            ("mini_pray_fixed", G.ALTAR, partial(make_action_and_confirm, command=A.Command.PRAY)),
            ("mini_sink_fixed", G.SINK, partial(make_action_and_confirm, command=A.Command.QUAFF)),
            ("mini_read_fixed", G.SCROLL_CLASS, partial(pickup_and_use_item, command=A.Command.READ)),
            ("mini_zap_fixed", G.WAND_CLASS, partial(pickup_and_use_item, command=A.Command.ZAP)),
            (
                "mini_puton_fixed",
                frozenset.union(G.AMULET_CLASS, G.RING_CLASS),
                partial(pickup_and_use_item, command=A.Command.PUTON),
            ),
            ("mini_wear_fixed", G.ARMOR_CLASS, partial(pickup_and_use_item, command=A.Command.WEAR)),
            ("mini_wield_fixed", G.WEAPON_CLASS, partial(pickup_and_use_item, command=A.Command.WIELD)),
        ],
    )
    @pytest.mark.parametrize("seed", [1])
    def test_mini_fixed(self, env, where, action, seed):
        # TODO: for some of the variants there are monsters which have to be dealt with
        # TODO: for some of the seeds there are items already worn, which have to be taken off
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        bot = Bot(cfg)
        bot.strategy(partial(general_mini, where=where, action=action))

        status = bot.main()
        assert status == bot.env.StepStatus.TASK_SUCCESSFUL

    @pytest.mark.parametrize("env", ["mini_locked_fixed"])
    @pytest.mark.parametrize("seed", [0])
    def test_mini_locked(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        bot = Bot(cfg)

        bot.strategy(open_doors_kick)
        bot.strategy(explore)
        bot.strategy(goto_stairs)

        status = bot.main()
        assert status == bot.env.StepStatus.TASK_SUCCESSFUL

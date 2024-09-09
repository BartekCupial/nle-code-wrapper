import pytest

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.plugins.strategy import Strategy
from nle_code_wrapper.plugins.strategy.strategies import (
    explore,
    explore_items,
    goto_items,
    goto_stairs,
    open_door,
    open_doors_key,
    pickup_items,
)


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize(
        "env, seed",
        [
            ("keyroom_small_fixed", 7),
            ("keyroom_small", 7),
            ("keyroom_big", 7),
        ],
    )
    def test_keyroom_easy(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", "--no-render", f"--seed={seed}"])
        bot = Bot(cfg)

        @Strategy.wrap
        def general_key(bot: "Bot"):
            stairs_strat = goto_stairs(bot)
            door_strat = open_door(bot)
            key_strat = open_doors_key(bot)
            explore_items_strat = explore_items(bot)
            pickup_items_strat = pickup_items(bot)
            explore_strat = explore(bot)

            while True:
                try:
                    stairs_strat()
                    explore_items_strat()
                    pickup_items_strat()
                    door_strat()
                    key_strat()
                    explore_strat()
                except BotPanic:
                    pass
                yield True

        bot.strategy(general_key)
        status = bot.main()
        assert status == bot.env.StepStatus.TASK_SUCCESSFUL

    @pytest.mark.parametrize(
        "env, seed",
        [
            ("keyroom_small_dark", 7),
            ("keyroom_big_dark", 7),
        ],
    )
    def test_keyroom_hard(self, env, seed):
        # TODO: this is quite weak strategy for general exploration of the levels

        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}"])
        bot = Bot(cfg)

        @Strategy.wrap
        def general_key(bot: "Bot"):
            stairs_strat = goto_stairs(bot)
            door_strat = open_door(bot)
            key_strat = open_doors_key(bot)
            goto_items_strat = goto_items(bot)
            pickup_items_strat = pickup_items(bot)
            explore_strat = explore(bot)

            while True:
                try:
                    if explore_strat():
                        pass
                    else:
                        stairs_strat()
                        goto_items_strat()
                        pickup_items_strat()
                        door_strat()
                        key_strat()
                except BotPanic:
                    pass
                yield True

        bot.strategy(general_key)
        status = bot.main()
        assert status == bot.env.StepStatus.TASK_SUCCESSFUL

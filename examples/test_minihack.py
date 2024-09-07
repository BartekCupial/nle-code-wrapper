import numpy as np

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components
from nle_code_wrapper.plugins.strategy import Strategy
from nle_code_wrapper.plugins.strategy.panics import entity_moved, lost_hp
from nle_code_wrapper.plugins.strategy.strategies import (
    explore,
    fight_all_monsters,
    fight_closest_monster,
    goto_stairs,
    open_door,
    random_move,
)


def main():
    register_minihack_components()
    cfg = parse_minihack_args()

    bot = Bot(cfg)

    @Strategy.wrap
    def general_strategy(bot: "Bot"):
        fight_strategy = fight_closest_monster(bot)
        goto_stairs_strategy = goto_stairs(bot)
        open_door_strategy = open_door(bot)
        exploration_strategy = explore(bot)

        while True:
            # 1) if there are reachable monsters fight them
            if fight_strategy():
                pass
            # 2) elif there are reachable stairs goto them
            elif goto_stairs_strategy():
                pass
            # 3) elif there are closed doors
            elif open_door_strategy():
                pass
            # 3) explore
            else:
                exploration_strategy()

            yield

    bot.strategy(general_strategy)

    # bot.panic(lost_hp)
    # bot.panic(entity_moved)
    # bot.strategy(open_door)
    # bot.strategy(fight_all_monsters)
    # bot.strategy(goto_stairs)
    # bot.strategy(explore)
    # bot.strategy(random_move)

    def run_bot():
        status = bot.main()
        succeess = status == bot.env.StepStatus.TASK_SUCCESSFUL
        if not succeess:
            print(f"seed: {cfg.seed} failed, status: {status.name}")

    if cfg.seed is not None:
        run_bot()
    else:
        for i in range(100):
            cfg.seed = i
            print(f"test bot on seed: {i}")
            run_bot()


if __name__ == "__main__":
    main()

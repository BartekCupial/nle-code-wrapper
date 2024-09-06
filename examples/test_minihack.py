import numpy as np

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components
from nle_code_wrapper.plugins.strategy.panics import lost_hp
from nle_code_wrapper.plugins.strategy.strategies import (
    explore,
    fight_all_monsters,
    goto_stairs,
    open_door,
    random_move,
)


def main():
    register_minihack_components()
    cfg = parse_minihack_args()

    bot = Bot(cfg)

    bot.panic(lost_hp)
    # bot.panic(monster_moved)
    # bot.strategy(open_door)
    bot.strategy(fight_all_monsters)
    bot.strategy(goto_stairs)
    bot.strategy(explore)
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

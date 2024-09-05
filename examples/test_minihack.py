import numpy as np

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components
from nle_code_wrapper.strategies import explore, goto_stairs, kill_all_monsters, open_doors


def main():
    register_minihack_components()
    cfg = parse_minihack_args()

    bot = Bot(cfg)

    bot.strategy(open_doors)
    bot.strategy(kill_all_monsters)
    bot.strategy(goto_stairs)
    bot.strategy(explore)

    init_seed = cfg.seed
    if init_seed:
        assert bot.main()
    else:
        for i in range(100):
            cfg.seed = i
            print(f"test bot on seed: {i}")
            assert bot.main()


if __name__ == "__main__":
    main()

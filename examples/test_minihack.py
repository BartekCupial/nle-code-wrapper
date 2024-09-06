import numpy as np

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components
from nle_code_wrapper.strategies import explore, fight_all_monsters, goto_stairs, open_door


def main():
    register_minihack_components()
    cfg = parse_minihack_args()

    bot = Bot(cfg)

    bot.strategy(open_door)
    bot.strategy(fight_all_monsters)
    bot.strategy(goto_stairs)
    bot.strategy(explore)

    init_seed = cfg.seed
    if init_seed is not None:
        assert bot.main()
    else:
        for i in range(100):
            cfg.seed = i
            print(f"test bot on seed: {i}")
            try:
                assert bot.main()
            except Exception:
                print(f"seed: {i} failed")
                pass


if __name__ == "__main__":
    main()

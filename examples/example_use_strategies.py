from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategies import descend_stairs, explore, fight_melee
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components


def main():
    register_minihack_components()
    cfg = parse_minihack_args(argv=["--env=big_room_dark"])
    bot = Bot(cfg)
    bot.strategy(fight_melee)
    bot.strategy(descend_stairs)
    bot.strategy(explore)
    bot.main()


if __name__ == "__main__":
    main()

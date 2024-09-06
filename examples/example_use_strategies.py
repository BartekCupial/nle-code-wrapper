from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components
from nle_code_wrapper.plugins.strategy.strategies import explore, fight_all_monsters, goto_stairs


def main():
    register_minihack_components()
    cfg = parse_minihack_args(argv=["--env=big_room_dark"])
    bot = Bot(cfg)
    bot.strategy(fight_all_monsters)
    bot.strategy(goto_stairs)
    bot.strategy(explore)
    bot.main()


if __name__ == "__main__":
    main()

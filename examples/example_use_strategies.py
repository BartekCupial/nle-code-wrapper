from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategies import explore, fight_closest_monster, goto_closest_staircase_down
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components


def main():
    register_minihack_components()
    cfg = parse_minihack_args(argv=["--env=big_room_dark"])
    bot = Bot(cfg)
    bot.strategy(fight_closest_monster)
    bot.strategy(goto_closest_staircase_down)
    bot.strategy(explore)
    bot.main()


if __name__ == "__main__":
    main()

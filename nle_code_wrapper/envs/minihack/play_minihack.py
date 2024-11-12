import os
import sys
import termios
import tty

from nle_utils.cfg.arguments import parse_args, parse_full_cfg
from nle_utils.envs.env_utils import register_env
from nle_utils.envs.minihack.minihack_env import MINIHACK_ENVS
from nle_utils.envs.minihack.minihack_params import add_extra_params_minihack_env
from nle_utils.play import play
from nle_utils.scripts.play_nethack import get_action as play_using_nethack

from nle_code_wrapper.cfg.cfg import add_code_wrapper_cli_args
from nle_code_wrapper.envs.minihack.minihack_env import make_minihack_env


def play_using_strategies(env, action_mode="human", obs=None):
    if action_mode == "random":
        action = env.action_space.sample()
    elif action_mode == "human":
        while True:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = os.read(fd, 3)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            if len(ch) == 1:
                if ord(ch) == 3:
                    raise KeyboardInterrupt
                else:
                    action = int(ch)

            try:
                assert action in env.action_space
                break
            except ValueError:
                print(f"Selected action '{ch}' is not in action list. " "Please try again.")
                continue

    return action


def register_minihack_envs():
    for env_name in MINIHACK_ENVS:
        register_env(env_name, make_minihack_env)


def register_minihack_components():
    register_minihack_envs()


def parse_minihack_args(argv=None):
    parser, partial_cfg = parse_args(argv=argv)
    add_extra_params_minihack_env(parser)
    add_code_wrapper_cli_args(parser)
    final_cfg = parse_full_cfg(parser, argv)
    return final_cfg


def main():
    register_minihack_components()
    cfg = parse_minihack_args()

    if cfg.code_wrapper:
        play(cfg, get_action=play_using_strategies)
    else:
        play(cfg, get_action=play_using_nethack)


if __name__ == "__main__":
    main()

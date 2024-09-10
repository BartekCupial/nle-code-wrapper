import contextlib
import os
import termios
import tty

from nle import nethack

from nle_code_wrapper.cfg.arguments import parse_args, parse_full_cfg
from nle_code_wrapper.envs.env_utils import register_env
from nle_code_wrapper.envs.minihack.minihack_env import MINIHACK_ENVS, make_minihack_env
from nle_code_wrapper.envs.minihack.minihack_params import add_extra_params_minihack_env
from nle_code_wrapper.play import play


@contextlib.contextmanager
def no_echo():
    tt = termios.tcgetattr(0)
    try:
        tty.setraw(0)
        yield
    finally:
        termios.tcsetattr(0, termios.TCSAFLUSH, tt)


def get_action(env, action_mode):
    if action_mode == "random":
        action = env.action_space.sample()
    elif action_mode == "human":
        while True:
            with no_echo():
                ch = ord(os.read(0, 1))
            if ch == nethack.C("c"):
                print("Received exit code {}. Aborting.".format(ch))
                return None
            try:
                action = env.actions.index(ch)
                break
            except ValueError:
                print(("Selected action '%s' is not in action list. " "Please try again.") % chr(ch))
                continue
    return action


def register_minihack_envs():
    for env_name in MINIHACK_ENVS.keys():
        register_env(env_name, make_minihack_env)


def register_minihack_components():
    register_minihack_envs()


def parse_minihack_args(argv=None):
    parser, partial_cfg = parse_args(argv=argv)
    add_extra_params_minihack_env(parser)
    final_cfg = parse_full_cfg(parser, argv)
    return final_cfg


def main():
    register_minihack_components()
    cfg = parse_minihack_args()
    play(cfg, get_action=get_action)


if __name__ == "__main__":
    main()

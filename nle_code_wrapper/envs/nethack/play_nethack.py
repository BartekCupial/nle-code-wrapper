from functools import partial

from nle_utils.cfg.arguments import parse_args, parse_full_cfg
from nle_utils.envs.env_utils import register_env
from nle_utils.envs.nethack.nethack_env import NETHACK_ENVS
from nle_utils.envs.nethack.nethack_params import add_extra_params_nethack_env
from nle_utils.play import play
from nle_utils.scripts.play_nethack import get_action as play_using_nethack

from nle_code_wrapper.cfg.cfg import add_code_wrapper_cli_args
from nle_code_wrapper.envs.nethack.nethack_env import make_nethack_env
from nle_code_wrapper.utils.play import completer, play_using_strategies_autocomplete, setup_autocomplete


def register_nethack_envs():
    for env_name in NETHACK_ENVS:
        register_env(env_name, make_nethack_env)


def register_nethack_components():
    register_nethack_envs()


def parse_nethack_args(argv=None):
    parser, partial_cfg = parse_args(argv=argv)
    add_extra_params_nethack_env(parser)
    add_code_wrapper_cli_args(parser)
    final_cfg = parse_full_cfg(parser, argv)
    return final_cfg


def main():
    register_nethack_components()
    cfg = parse_nethack_args()

    if cfg.code_wrapper:
        setup_autocomplete(partial(completer, commands=cfg.strategies))
        play(cfg, get_action=play_using_strategies_autocomplete)
    else:
        play(cfg, get_action=play_using_nethack)


if __name__ == "__main__":
    main()

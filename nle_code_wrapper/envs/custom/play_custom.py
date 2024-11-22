from nle_utils.cfg.arguments import parse_args, parse_full_cfg
from nle_utils.envs.env_utils import register_env
from nle_utils.envs.minihack.minihack_params import add_extra_params_minihack_env
from nle_utils.play import play
from nle_utils.scripts.play_nethack import get_action as play_using_nethack

from nle_code_wrapper.cfg.cfg import add_code_wrapper_cli_args
from nle_code_wrapper.envs.custom.custom_env import CUSTOM_ENVS, make_custom_env
from nle_code_wrapper.utils.play import play_using_strategies


def register_custom_envs():
    for env_name in CUSTOM_ENVS:
        register_env(env_name, make_custom_env)


def register_custom_components():
    register_custom_envs()


def parse_custom_args(argv=None):
    parser, partial_cfg = parse_args(argv=argv)
    add_extra_params_minihack_env(parser)
    add_code_wrapper_cli_args(parser)
    final_cfg = parse_full_cfg(parser, argv)
    return final_cfg


def main():
    register_custom_components()
    cfg = parse_custom_args()

    if cfg.code_wrapper:
        play(cfg, get_action=play_using_strategies)
    else:
        play(cfg, get_action=play_using_nethack)


if __name__ == "__main__":
    main()

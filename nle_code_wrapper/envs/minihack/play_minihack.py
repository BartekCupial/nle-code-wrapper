from nle_utils.cfg.arguments import parse_args, parse_full_cfg
from nle_utils.envs.env_utils import register_env
from nle_utils.envs.minihack.minihack_env import MINIHACK_ENVS
from nle_utils.envs.minihack.minihack_params import add_extra_params_minihack_env
from nle_utils.play import play
from nle_utils.scripts.play_nethack import get_action

from nle_code_wrapper.cfg.cfg import add_code_wrapper_cli_args
from nle_code_wrapper.envs.minihack.minihack_env import make_minihack_env


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
    play(cfg, get_action=get_action)


if __name__ == "__main__":
    main()

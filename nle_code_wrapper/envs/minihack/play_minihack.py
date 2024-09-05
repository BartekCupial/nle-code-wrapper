from nle_code_wrapper.cfg.arguments import parse_args, parse_full_cfg
from nle_code_wrapper.envs.env_utils import register_env
from nle_code_wrapper.envs.minihack.minihack_env import MINIHACK_ENVS, make_minihack_env
from nle_code_wrapper.envs.minihack.minihack_params import add_extra_params_minihack_env
from nle_code_wrapper.envs.play import play


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
    play(cfg)


if __name__ == "__main__":
    main()

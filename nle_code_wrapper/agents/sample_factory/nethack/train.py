import sys

from nle_utils.envs.nethack.nethack_params import add_extra_params_nethack_env
from sample_factory.algo.utils.context import global_model_factory
from sample_factory.cfg.arguments import parse_full_cfg, parse_sf_args
from sample_factory.envs.env_utils import register_env
from sample_factory.model.encoder import Encoder
from sample_factory.train import run_rl
from sample_factory.utils.typing import Config, ObsSpace

from nle_code_wrapper.agents.sample_factory.minihack.minihack_params import (
    add_extra_params_general,
    add_extra_params_model,
    minihack_override_defaults,
)
from nle_code_wrapper.agents.sample_factory.minihack.train import make_minihack_encoder
from nle_code_wrapper.agents.sample_factory.nethack.nethack_env import NETHACK_ENVS, make_nethack_env
from nle_code_wrapper.cfg.cfg import add_code_wrapper_cli_args


def register_nethack_envs():
    for env_name in NETHACK_ENVS:
        register_env(env_name, make_nethack_env)


def make_nethack_encoder(cfg: Config, obs_space: ObsSpace) -> Encoder:
    """Factory function as required by the API."""
    return make_minihack_encoder(cfg, obs_space)


def register_nethack_components():
    register_nethack_envs()
    global_model_factory().register_encoder_factory(make_nethack_encoder)


def parse_nethack_args(argv=None, evaluation=False):
    parser, partial_cfg = parse_sf_args(argv=argv, evaluation=evaluation)
    add_extra_params_nethack_env(parser)
    add_extra_params_model(parser)
    add_extra_params_general(parser)
    add_code_wrapper_cli_args(parser)
    minihack_override_defaults(partial_cfg.env, parser)
    final_cfg = parse_full_cfg(parser, argv)

    return final_cfg


def main():  # pragma: no cover
    """Script entry point."""
    register_nethack_components()
    cfg = parse_nethack_args()
    status = run_rl(cfg)
    return status


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

import sys

from nle_utils.envs.nethack.nethack_params import add_extra_params_nethack_env
from sample_factory.cfg.arguments import parse_full_cfg, parse_sf_args
from sample_factory.random import enjoy

from nle_code_wrapper.agents.sample_factory.minihack.minihack_params import (
    add_extra_params_general,
    add_extra_params_model,
    minihack_override_defaults,
)
from nle_code_wrapper.agents.sample_factory.nethack.train import register_nethack_components
from nle_code_wrapper.cfg.cfg import add_code_wrapper_cli_args


def main():  # pragma: no cover
    """Script entry point."""
    register_nethack_components()

    parser, cfg = parse_sf_args(evaluation=True)
    add_extra_params_nethack_env(parser)
    add_extra_params_model(parser)
    add_extra_params_general(parser)
    add_code_wrapper_cli_args(parser)
    minihack_override_defaults(cfg.env, parser)
    cfg = parse_full_cfg(parser)

    status = enjoy(cfg)
    return status


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

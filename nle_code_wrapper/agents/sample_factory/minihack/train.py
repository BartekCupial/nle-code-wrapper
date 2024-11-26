import sys

from nle_utils.envs.minihack.minihack_env import MINIHACK_ENVS
from nle_utils.envs.minihack.minihack_params import add_extra_params_minihack_env
from sample_factory.algo.utils.context import global_model_factory
from sample_factory.cfg.arguments import parse_full_cfg, parse_sf_args
from sample_factory.envs.env_utils import register_env
from sample_factory.model.encoder import Encoder
from sample_factory.train import run_rl
from sample_factory.utils.typing import Config, ObsSpace

from nle_code_wrapper.agents.sample_factory.minihack.minihack_env import make_minihack_env
from nle_code_wrapper.agents.sample_factory.minihack.minihack_params import (
    add_extra_params_general,
    add_extra_params_model,
    minihack_override_defaults,
)
from nle_code_wrapper.agents.sample_factory.minihack.models import MODELS_LOOKUP
from nle_code_wrapper.cfg.cfg import add_code_wrapper_cli_args, add_skill_wrapper_cli_args


def register_minihack_envs():
    for env_name in MINIHACK_ENVS:
        register_env(env_name, make_minihack_env)


def make_minihack_encoder(cfg: Config, obs_space: ObsSpace, ignore_option: bool = False) -> Encoder:
    """Factory function as required by the API."""
    try:
        model_cls = MODELS_LOOKUP[cfg.model]
    except KeyError:
        raise NotImplementedError("model=%s" % cfg.model) from None

    return model_cls(cfg, obs_space, ignore_option=ignore_option)


def register_minihack_components():
    register_minihack_envs()
    global_model_factory().register_encoder_factory(make_minihack_encoder)


def parse_minihack_args(argv=None, evaluation=False):
    parser, partial_cfg = parse_sf_args(argv=argv, evaluation=evaluation)
    add_extra_params_minihack_env(parser)
    add_extra_params_model(parser)
    add_extra_params_general(parser)
    add_code_wrapper_cli_args(parser)
    add_skill_wrapper_cli_args(parser)
    minihack_override_defaults(partial_cfg.env, parser)
    final_cfg = parse_full_cfg(parser, argv)

    return final_cfg


def delete_nle_folders_in_tmp():
    import os
    import shutil

    tmp_dir = "/tmp"
    prefix = "nle"

    try:
        # List all directory entries in the /tmp directory
        for entry in os.listdir(tmp_dir):
            full_path = os.path.join(tmp_dir, entry)

            # Check if the entry is a directory and starts with the desired prefix
            if os.path.isdir(full_path) and entry.startswith(prefix):
                # Delete the directory
                shutil.rmtree(full_path)
                print(f"Deleted: {full_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def main():  # pragma: no cover
    """Script entry point."""
    # delete_nle_folders_in_tmp()

    register_minihack_components()
    cfg = parse_minihack_args()
    status = run_rl(cfg)
    return status


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

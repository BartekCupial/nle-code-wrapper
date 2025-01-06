import sys

from nle_utils.envs.minihack.minihack_env import MINIHACK_ENVS
from nle_utils.envs.minihack.minihack_params import add_extra_params_minihack_env
from sample_factory.algo.utils.context import global_model_factory
from sample_factory.cfg.arguments import parse_full_cfg, parse_sf_args
from sample_factory.envs.env_utils import register_env
from sample_factory.model.actor_critic import LMActorCriticSeparateWeights
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
from nle_code_wrapper.cfg.cfg import add_code_wrapper_cli_args


def register_minihack_envs():
    for env_name in MINIHACK_ENVS:
        register_env(env_name, make_minihack_env)


def make_minihack_encoder(cfg: Config, obs_space: ObsSpace) -> Encoder:
    """Factory function as required by the API."""
    try:
        model_cls = MODELS_LOOKUP[cfg.model]
    except KeyError:
        raise NotImplementedError("model=%s" % cfg.model) from None

    return model_cls(cfg, obs_space)


def register_minihack_components(cfg):
    register_minihack_envs()
    global_model_factory().register_encoder_factory(make_minihack_encoder)

    if cfg.use_lm:
        global_model_factory().register_actor_critic_factory(LMActorCriticSeparateWeights)


def parse_minihack_args(argv=None, evaluation=False):
    parser, partial_cfg = parse_sf_args(argv=argv, evaluation=evaluation)
    add_extra_params_minihack_env(parser)
    add_extra_params_model(parser)
    add_extra_params_general(parser)
    add_code_wrapper_cli_args(parser)
    minihack_override_defaults(partial_cfg.env, parser)
    final_cfg = parse_full_cfg(parser, argv)

    return final_cfg


def main():  # pragma: no cover
    """Script entry point."""
    cfg = parse_minihack_args()
    register_minihack_components(cfg)
    status = run_rl(cfg)
    return status


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

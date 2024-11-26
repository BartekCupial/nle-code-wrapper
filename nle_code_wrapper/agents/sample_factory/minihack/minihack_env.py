from typing import Optional

from nle_utils.envs.minihack.minihack_env import make_minihack_env as make_env

from nle_code_wrapper.agents.sample_factory.minihack.wrappers import AddChanngelDim
from nle_code_wrapper.utils.utils import get_function_by_name
from nle_code_wrapper.wrappers.nle_code_wrapper import NLECodeWrapper
from nle_code_wrapper.wrappers.skill_wrapper import SkillWrapper


def make_minihack_env(env_name, cfg, env_config, render_mode: Optional[str] = None):
    # rgb_array is currently not supported in MiniHack
    if render_mode == "rgb_array":
        render_mode = None

    env = make_env(env_name=env_name, cfg=cfg, env_config=env_config, render_mode=render_mode)

    strategies = []
    for strategy_name in cfg.strategies:
        strategy_func = get_function_by_name(cfg.strategies_loc, strategy_name)
        strategies.append(strategy_func)

    if cfg.code_wrapper:
        env = NLECodeWrapper(env, strategies)

    if cfg.model == "default_make_encoder_func":
        env = AddChanngelDim(env)

    if cfg.skill_wrapper:
        env = SkillWrapper(env, cfg.skill_dim, cfg.skill_type)

    return env

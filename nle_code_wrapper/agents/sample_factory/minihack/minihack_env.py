from typing import Optional

from nle_utils.envs.minihack.minihack_env import make_minihack_env as make_env

from nle_code_wrapper.agents.sample_factory.minihack.wrappers import AddChanngelDim
from nle_code_wrapper.utils.utils import get_function_by_name
from nle_code_wrapper.wrappers.nle_code_wrapper import NLECodeWrapper


def make_minihack_env(env_name, cfg, env_config, render_mode: Optional[str] = None):
    env = make_env(env_name=env_name, cfg=cfg, env_config=env_config, render_mode=render_mode)

    strategies = []
    for strategy_name in cfg.strategies:
        strategy_func = get_function_by_name(cfg.strategies_loc, strategy_name)
        strategies.append(strategy_func)

    panics = []
    for panic_name in cfg.panics:
        panic_func = get_function_by_name(cfg.panics_loc, panic_name)
        panics.append(panic_func)

    if cfg.code_wrapper:
        env = NLECodeWrapper(env, strategies, max_strategy_steps=cfg.max_strategy_steps, gamma=cfg.gamma)

    if cfg.model == "default_make_encoder_func":
        env = AddChanngelDim(env)

    return env

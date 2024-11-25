import inspect
from typing import Optional

from nle_utils.envs.nethack.nethack_env import make_nethack_env as make_env

import nle_code_wrapper.bot.strategies as strategy_module
from nle_code_wrapper.utils.utils import get_function_by_name
from nle_code_wrapper.wrappers.nle_code_wrapper import NLECodeWrapper


def make_nethack_env(env_name, cfg, env_config, render_mode: Optional[str] = None):
    env = make_env(env_name=env_name, cfg=cfg, env_config=env_config, render_mode=render_mode)

    if len(cfg.strategies) > 0:
        if isinstance(cfg.strategies[0], str):
            strategies = []
            for strategy_name in cfg.strategies:
                strategy_func = get_function_by_name(cfg.strategies_loc, strategy_name)
                strategies.append(strategy_func)
            cfg.strategies = strategies
    else:
        cfg.strategies = [obj for name, obj in inspect.getmembers(strategy_module, inspect.isfunction)]

    if cfg.code_wrapper:
        env = NLECodeWrapper(env, cfg.strategies, max_strategy_steps=cfg.max_strategy_steps, gamma=cfg.gamma)

    return env

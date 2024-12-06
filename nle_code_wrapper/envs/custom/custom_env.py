import inspect
from typing import Optional

import gym
from nle_utils.envs.minihack.minihack_env import make_minihack_env as make_env

import nle_code_wrapper.bot.panics as panic_module
import nle_code_wrapper.bot.strategies as strategy_module
import nle_code_wrapper.envs.custom.envs  # noqa: E402
from nle_code_wrapper.utils.utils import get_function_by_name
from nle_code_wrapper.wrappers.nle_code_wrapper import NLECodeWrapper

CUSTOM_ENVS = []
for env_spec in gym.envs.registry.all():
    id = env_spec.id
    if id.split("-")[0] == "CustomMiniHack":
        CUSTOM_ENVS.append(id)


def make_custom_env(env_name, cfg, env_config, render_mode: Optional[str] = None):
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

    if len(cfg.panics) > 0:
        if isinstance(cfg.panics[0], str):
            panics = []
            for panic_name in cfg.panics:
                panic_func = get_function_by_name(cfg.panics_loc, panic_name)
                panics.append(panic_func)
            cfg.panics = panics
    else:
        cfg.panics = [obj for name, obj in inspect.getmembers(panic_module, inspect.isfunction)]

    if cfg.code_wrapper:
        gamma = cfg.gamma if hasattr(cfg, "gamma") else 1.0
        env = NLECodeWrapper(env, cfg.strategies, cfg.panics, max_strategy_steps=cfg.max_strategy_steps, gamma=gamma)

    return env

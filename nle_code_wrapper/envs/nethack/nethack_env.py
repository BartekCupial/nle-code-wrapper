import inspect
from typing import Optional, Tuple

import gym
import nle  # NOQA: F401
from nle import nethack
from nle.nethack import NETHACKOPTIONS
from nle_utils.wrappers import GymV21CompatibilityV0, NLETimeLimit

import nle_code_wrapper.bot.panics as panic_module
import nle_code_wrapper.bot.strategies as strategy_module
from nle_code_wrapper.utils.utils import get_function_by_name
from nle_code_wrapper.wrappers.nle_code_wrapper import NLECodeWrapper


def make_nethack_env(env_name, cfg, env_config, render_mode: Optional[str] = None):
    observation_keys = (
        "message",
        "blstats",
        "tty_chars",
        "tty_colors",
        "tty_cursor",
        # ALSO AVAILABLE (OFF for speed)
        # "specials",
        # "colors",
        # "chars",
        "glyphs",
        "inv_glyphs",
        "inv_strs",
        "inv_letters",
        "inv_oclasses",
    )

    # NetHack options
    # Copy & swap out "pickup_types".
    options = []
    for option in nethack.NETHACKOPTIONS:
        if option.startswith("pickup_types"):
            options.append("pickup_types:$")
            continue
        options.append(option)

    if not cfg.autopickup:
        options += ("!autopickup",)
    if not cfg.pet:
        options += ("pettype:none",)

    kwargs = dict(
        observation_keys=observation_keys,
        penalty_step=cfg.penalty_step,
        penalty_time=cfg.penalty_time,
        penalty_mode=cfg.fn_penalty_step,
        savedir=cfg.savedir,
        save_ttyrec_every=cfg.save_ttyrec_every,
        actions=nethack.ACTIONS,
        options=options,
    )

    param_mapping = {
        "max_episode_steps": cfg.max_episode_steps,
        "character": cfg.character,
        "allow_all_yn_questions": cfg.allow_all_yn_questions,
        "allow_all_modes": cfg.allow_all_modes,
    }

    for param_name, param_value in param_mapping.items():
        if param_value is not None:
            kwargs[param_name] = param_value

    env = gym.make(env_name, **kwargs)

    # wrap NLE with timeout
    env = NLETimeLimit(env)

    env = GymV21CompatibilityV0(env=env, render_mode=render_mode)

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
        env = NLECodeWrapper(
            env,
            cfg.strategies,
            cfg.panics,
            max_strategy_steps=cfg.max_strategy_steps,
            add_letter_strategies=cfg.add_letter_strategies,
            add_direction_strategies=cfg.add_direction_strategies,
            add_more_strategy=cfg.add_more_strategy,
            gamma=gamma,
        )

    return env

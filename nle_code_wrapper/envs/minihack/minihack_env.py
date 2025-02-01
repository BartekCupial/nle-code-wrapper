import inspect
from os.path import join
from typing import Optional

import gym
import minihack  # NOQA: F401
from nle.env.base import FULL_ACTIONS
from nle_utils.wrappers import AutoMore, GymV21CompatibilityV0, NLETimeLimit, NoProgressAbort, SingleSeed
from sample_factory.utils.utils import ensure_dir_exists, experiment_dir

import nle_code_wrapper.bot.panics as panic_module
import nle_code_wrapper.bot.strategies as strategy_module
import nle_code_wrapper.envs.minihack.envs  # noqa: E402
from nle_code_wrapper.utils.utils import get_function_by_name
from nle_code_wrapper.wrappers import NLECodeWrapper, NoProgressFeedback, SaveOnException

MINIHACK_ENVS = []
for env_spec in gym.envs.registry.all():
    id = env_spec.id
    if id.split("-")[0] == "MiniHack":
        MINIHACK_ENVS.append(id)

CUSTOM_ENVS = []
for env_spec in gym.envs.registry.all():
    id = env_spec.id
    if id.split("-")[0] == "CustomMiniHack":
        CUSTOM_ENVS.append(id)


def make_minihack_env(env_name, cfg, env_config, render_mode: Optional[str] = None):
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

    kwargs = dict(
        observation_keys=observation_keys,
        penalty_step=cfg.penalty_step,
        penalty_time=cfg.penalty_time,
        penalty_mode=cfg.fn_penalty_step,
        savedir=cfg.savedir,
        save_ttyrec_every=cfg.save_ttyrec_every,
        actions=FULL_ACTIONS,
    )

    param_mapping = {
        "max_episode_steps": cfg.max_episode_steps,
        "character": cfg.character,
        "autopickup": cfg.autopickup,
        "allow_all_yn_questions": cfg.allow_all_yn_questions,
        "allow_all_modes": cfg.allow_all_modes,
    }

    for param_name, param_value in param_mapping.items():
        if param_value is not None:
            kwargs[param_name] = param_value

    env = gym.make(env_name, **kwargs)
    env = NoProgressAbort(env)
    env = AutoMore(env)

    env = NLETimeLimit(env)

    env = GymV21CompatibilityV0(env=env, render_mode=render_mode)

    if cfg.single_seed:
        env = SingleSeed(env, cfg.single_seed)

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
        env = NoProgressFeedback(env)

    if cfg.save_on_exception:
        failed_game_path = join(experiment_dir(cfg=cfg), "failed_games")
        ensure_dir_exists(failed_game_path)
        env = SaveOnException(env, failed_game_path=failed_game_path)

    return env

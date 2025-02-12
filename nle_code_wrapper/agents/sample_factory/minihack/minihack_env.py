from os.path import join
from typing import Optional

import gym
import minihack  # NOQA: F401
from nle import nethack
from nle_utils.wrappers import (
    AutoMore,
    GymV21CompatibilityV0,
    NLETimeLimit,
    NoProgressAbort,
    ObservationFilterWrapper,
    PrevActionsWrapper,
    SingleSeed,
    TileTTY,
)
from nle_utils.wrappers.nle_tokenizer import NLETokenizer
from sample_factory.utils.utils import ensure_dir_exists, experiment_dir

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

    if cfg.code_wrapper:
        kwargs["actions"] = nethack.ACTIONS

    env = gym.make(env_name, **kwargs)
    env = NoProgressAbort(env)

    if cfg.code_wrapper:
        env = AutoMore(env)

    if cfg.add_image_observation:
        env = TileTTY(
            env,
            crop_size=cfg.crop_dim,
            rescale_font_size=(cfg.pixel_size, cfg.pixel_size),
        )

    if cfg.use_prev_action:
        env = PrevActionsWrapper(env)

    # wrap NLE with timeout
    env = NLETimeLimit(env)

    env = GymV21CompatibilityV0(env=env, render_mode=render_mode)

    if cfg.single_seed:
        env = SingleSeed(env, cfg.single_seed)

    strategies = []
    for strategy_name in cfg.strategies:
        strategy_func = get_function_by_name(cfg.strategies_loc, strategy_name)
        strategies.append(strategy_func)

    panics = []
    for panic_name in cfg.panics:
        panic_func = get_function_by_name(cfg.panics_loc, panic_name)
        panics.append(panic_func)

    if cfg.code_wrapper:
        env = NLECodeWrapper(
            env,
            strategies,
            panics,
            max_strategy_steps=cfg.max_strategy_steps,
            add_letter_strategies=cfg.add_letter_strategies,
            add_direction_strategies=cfg.add_direction_strategies,
            add_more_strategy=cfg.add_more_strategy,
            gamma=cfg.gamma,
        )
        env = NoProgressFeedback(env)

    if cfg.tokenize_keys:
        env = NLETokenizer(env, max_token_length=cfg.max_token_length, tokenize_keys=cfg.tokenize_keys)

    if cfg.obs_keys:
        env = ObservationFilterWrapper(env, cfg.obs_keys)

    if cfg.save_on_exception:
        failed_game_path = join(experiment_dir(cfg=cfg), "failed_games")
        ensure_dir_exists(failed_game_path)
        env = SaveOnException(env, failed_game_path=failed_game_path)

    return env

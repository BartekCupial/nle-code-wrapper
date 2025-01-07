from typing import Optional, Tuple

import gym
import nle  # NOQA: F401
from nle import nethack
from nle.nethack import NETHACKOPTIONS
from nle_utils.wrappers import GymV21CompatibilityV0, NLETimeLimit

import nle_code_wrapper.bot.panics as panic_module
import nle_code_wrapper.bot.strategies as strategy_module
from nle_code_wrapper.agents.sample_factory.minihack.wrappers.add_channel_dim import AddChanngelDim
from nle_code_wrapper.utils.utils import get_function_by_name
from nle_code_wrapper.wrappers.nle_code_wrapper import NLECodeWrapper

NETHACK_ENVS = []
for env_spec in gym.envs.registry.all():
    id = env_spec.id
    if id.startswith("NetHack"):
        NETHACK_ENVS.append(id)


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

    kwargs = dict(
        observation_keys=observation_keys,
        penalty_step=cfg.penalty_step,
        penalty_time=cfg.penalty_time,
        penalty_mode=cfg.fn_penalty_step,
        savedir=cfg.savedir,
        save_ttyrec_every=cfg.save_ttyrec_every,
        wizard=False,
        allow_all_yn_questions=True,
        allow_all_modes=True,
        actions=nethack.ACTIONS,
    )

    if cfg.max_episode_steps is not None:
        kwargs["max_episode_steps"] = cfg.max_episode_steps

    if cfg.character is not None:
        kwargs["character"] = cfg.character

    # NetHack options
    options: Tuple = NETHACKOPTIONS
    if not cfg.autopickup:
        options += ("!autopickup",)
    if not cfg.pet:
        options += ("pettype:none",)
    kwargs["options"] = kwargs.pop("options", options)

    env = gym.make(env_name, **kwargs)

    # wrap NLE with timeout
    env = NLETimeLimit(env)

    env = GymV21CompatibilityV0(env=env, render_mode=render_mode)

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

    if cfg.model == "default_make_encoder_func":
        env = AddChanngelDim(env)

    return env

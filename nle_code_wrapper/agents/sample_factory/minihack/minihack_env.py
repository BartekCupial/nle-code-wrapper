import inspect
from typing import Optional

import gym
import minihack  # NOQA: F401
from nle.env.base import FULL_ACTIONS
from nle_utils.wrappers import GymV21CompatibilityV0, NLETimeLimit

import nle_code_wrapper.bot.panics as panic_module
import nle_code_wrapper.bot.strategies as strategy_module
from nle_code_wrapper.agents.sample_factory.minihack.wrappers.add_channel_dim import AddChanngelDim
from nle_code_wrapper.utils.utils import get_function_by_name
from nle_code_wrapper.wrappers.nle_code_wrapper import NLECodeWrapper

MINIHACK_ENVS = []
for env_spec in gym.envs.registry.all():
    id = env_spec.id
    if id.split("-")[0] == "MiniHack":
        MINIHACK_ENVS.append(id)


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

    if cfg.max_episode_steps is not None:
        kwargs["max_episode_steps"] = cfg.max_episode_steps

    if cfg.character is not None:
        kwargs["character"] = cfg.character

    if cfg.autopickup is not None:
        kwargs["autopickup"] = cfg.autopickup

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
        env = NLECodeWrapper(env, strategies, panics, max_strategy_steps=cfg.max_strategy_steps, gamma=cfg.gamma)

    if cfg.model == "default_make_encoder_func":
        env = AddChanngelDim(env)

    return env

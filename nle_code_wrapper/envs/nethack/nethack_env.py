from typing import Callable, List, Optional

from nle_utils.envs.nethack.nethack_env import make_nethack_env as make_env

from nle_code_wrapper.wrappers.nle_code_wrapper import NLECodeWrapper


def make_nethack_env(env_name, cfg, env_config, render_mode: Optional[str] = None, strategies: List[Callable] = []):
    env = make_env(env_name=env_name, cfg=cfg, env_config=env_config, render_mode=render_mode)

    if cfg.code_wrapper:
        env = NLECodeWrapper(env, strategies)

    return env

from nle_code_wrapper.utils.context import global_env_registry
from nle_code_wrapper.utils.typing import CreateEnvFunc
from nle_code_wrapper.utils.utils import log


def register_env(env_name: str, make_env_func: CreateEnvFunc) -> None:
    """
    Register a callable that creates an environment.
    This callable is called like:
        make_env_func(full_env_name, cfg, env_config)
        Where full_env_name is the name of the environment to be created, cfg is a namespace or AttrDict containing
        necessary configuration parameters and env_config is an auxiliary dictionary containing information such as worker index on which the environment lives
        (some envs may require this information)
    env_name: name of the environment
    make_env_func: callable that creates an environment
    """

    env_registry = global_env_registry()

    if env_name in env_registry:
        log.warning(f"Environment {env_name} already registered, overwriting...")

    assert callable(make_env_func), f"{make_env_func=} must be callable"

    env_registry[env_name] = make_env_func

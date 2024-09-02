from typing import Dict

from nle_code_wrapper.utils.typing import CreateEnvFunc


class GlobalContext:
    def __init__(self):
        self.env_registry = dict()


GLOBAL_CONTEXT = None


def global_context() -> GlobalContext:
    global GLOBAL_CONTEXT
    if GLOBAL_CONTEXT is None:
        GLOBAL_CONTEXT = GlobalContext()
    return GLOBAL_CONTEXT


def set_global_context(ctx: GlobalContext):
    global GLOBAL_CONTEXT
    GLOBAL_CONTEXT = ctx


def reset_global_context():
    global GLOBAL_CONTEXT
    GLOBAL_CONTEXT = GlobalContext()


def global_env_registry() -> Dict[str, CreateEnvFunc]:
    """
    :return: global env registry
    :rtype: EnvRegistry
    """
    return global_context().env_registry

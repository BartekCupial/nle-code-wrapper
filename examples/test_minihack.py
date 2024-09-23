import importlib
from functools import partial

from nle_utils.play import play

from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components


def get_function_by_name(module_name, function_name):
    try:
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        if callable(function):
            return function
        else:
            raise AttributeError(f"{function_name} is not a callable function in {module_name}")
    except ImportError:
        raise ImportError(f"Module {module_name} not found")
    except AttributeError:
        raise AttributeError(f"Function {function_name} not found in module {module_name}")


def main():
    register_minihack_components()
    cfg = parse_minihack_args()

    strategies = []
    for strategy_name in cfg.strategies:
        strategy_func = get_function_by_name("nle_code_wrapper.bot.strategy.strategies", strategy_name)
        strategies.append(strategy_func)

    play_random_strategy = partial(play, strategies=strategies)

    def run_bot():
        status = play_random_strategy(cfg)
        succeess = status == "TASK_SUCCESSFUL"
        if not succeess:
            print(f"seed: {cfg.seed if cfg.seed else 'None'} failed, status: {status}")

    if cfg.seed is not None:
        run_bot()
    else:
        for i in range(100):
            cfg.seed = i
            print(f"test bot on seed: {i}")
            run_bot()


if __name__ == "__main__":
    main()

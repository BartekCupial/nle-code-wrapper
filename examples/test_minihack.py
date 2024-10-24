from nle_utils.play import play

from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components
from nle_code_wrapper.utils.utils import get_function_by_name


def main():
    register_minihack_components()
    cfg = parse_minihack_args()

    strategies = []
    for strategy_name in cfg.strategies:
        strategy_func = get_function_by_name(cfg.strategies_loc, strategy_name)
        strategies.append(strategy_func)
    cfg.strategies = strategies

    def run_bot():
        status = play(cfg)
        succeess = status["end_status"].name == "TASK_SUCCESSFUL"
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

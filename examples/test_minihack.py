from functools import partial

from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args, register_minihack_components
from nle_code_wrapper.play import play


def get_action(env, mode):
    return env.action_space.sample()


def main():
    register_minihack_components()
    cfg = parse_minihack_args()
    play_random_strategy = partial(play, get_action=get_action)

    def run_bot():
        status = play_random_strategy(cfg)
        succeess = status == "TASK_SUCCESSFUL"
        if not succeess:
            print(f"seed: {cfg.seed} failed, status: {status.name}")

    if cfg.seed is not None:
        run_bot()
    else:
        for i in range(100):
            cfg.seed = i
            print(f"test bot on seed: {i}")
            run_bot()


if __name__ == "__main__":
    main()

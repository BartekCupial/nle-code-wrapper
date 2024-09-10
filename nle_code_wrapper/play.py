import timeit

from nle_code_wrapper.envs.create_env import create_env
from nle_code_wrapper.utils.attr_dict import AttrDict


def get_random_action(env, mode):
    return env.action_space.sample()


def play(cfg, get_action=get_random_action, strategies=[]):
    render_mode = "human"
    if cfg.no_render:
        render_mode = None

    env = create_env(
        cfg.env,
        cfg=cfg,
        env_config=AttrDict(worker_index=0, vector_index=0, env_id=0),
        render_mode=render_mode,
        strategies=strategies,
    )

    obs, info = env.reset(seed=cfg.seed)

    steps = 0
    reward = 0.0
    total_reward = 0.0
    action = None

    total_start_time = timeit.default_timer()
    start_time = total_start_time

    while True:
        action = get_action(env, cfg.play_mode)
        if action is None:
            break

        obs, reward, terminated, truncated, info = env.step(action)

        steps += 1
        total_reward += reward

        if not (terminated or truncated):
            continue

        time_delta = timeit.default_timer() - start_time

        if cfg.verbose:
            print("Final reward:", reward)
            print("End status:", info["end_status"].name)
            print(f"Total reward: {total_reward}, Steps: {steps}, SPS: {steps / time_delta}", total_reward)

        break
    env.close()

    return info["end_status"].name

import timeit

from nle_code_wrapper.envs.create_env import create_env
from nle_code_wrapper.utils.attr_dict import AttrDict
from nle_code_wrapper.wrappers.nle_code_wrapper import NLECodeWrapper


def get_action(env, mode):
    return env.action_space.sample()


def main(cfg):
    render_mode = "human"
    if cfg.no_render:
        render_mode = None

    env = create_env(
        cfg.env,
        cfg=cfg,
        env_config=AttrDict(worker_index=0, vector_index=0, env_id=0),
        render_mode=render_mode,
    )
    env = NLECodeWrapper(env)

    obs, info = env.reset()

    strategy_steps = 0
    steps = 0
    reward = 0.0
    total_reward = 0.0
    action = None

    total_start_time = timeit.default_timer()
    start_time = total_start_time

    while True:
        action = get_action(env, "random")
        if action is None:
            break

        obs, reward, terminated, truncated, info = env.step(action)
        strategy_steps += 1
        steps += info["steps"]
        total_reward += reward

        if not (terminated or truncated):
            continue

        time_delta = timeit.default_timer() - start_time

        print("Final reward:", reward)
        print("End status:", info["end_status"].name)
        print(f"Total reward: {total_reward}, Steps: {steps}, SPS: {steps / time_delta}", total_reward)
        break
    env.close()

    return info["end_status"].name

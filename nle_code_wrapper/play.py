import contextlib
import os
import termios
import timeit
import tty

import minihack  # noqa: F401
import nle  # noqa: F401
from nle import nethack

from nle_code_wrapper.envs.create_env import create_env
from nle_code_wrapper.utils.attr_dict import AttrDict


@contextlib.contextmanager
def no_echo():
    tt = termios.tcgetattr(0)
    try:
        tty.setraw(0)
        yield
    finally:
        termios.tcsetattr(0, termios.TCSAFLUSH, tt)


def get_action(env, action_mode):
    if action_mode == "random":
        action = env.action_space.sample()
    elif action_mode == "human":
        while True:
            with no_echo():
                ch = ord(os.read(0, 1))
            if ch == nethack.C("c"):
                print("Received exit code {}. Aborting.".format(ch))
                return None
            try:
                action = env.actions.index(ch)
                break
            except ValueError:
                print(("Selected action '%s' is not in action list. " "Please try again.") % chr(ch))
                continue
    return action


def play(cfg):
    render_mode = "human"
    if cfg.no_render:
        render_mode = None

    env = create_env(
        cfg.env,
        cfg=cfg,
        env_config=AttrDict(worker_index=0, vector_index=0, env_id=0),
        render_mode=render_mode,
    )

    steps = 0
    episodes = 0
    reward = 0.0
    action = None

    mean_sps = 0
    mean_reward = 0.0

    total_start_time = timeit.default_timer()
    start_time = total_start_time

    while True:
        action = get_action(env, cfg.play_mode)
        if action is None:
            break

        obs, reward, terminated, truncated, info = env.step(action)
        steps += 1
        mean_reward += (reward - mean_reward) / steps

        if not (terminated or truncated):
            continue

        time_delta = timeit.default_timer() - start_time

        print("Final reward:", reward)
        print("End status:", info["end_status"].name)
        print("Mean reward:", mean_reward)

        sps = steps / time_delta
        print("Episode: %i. Steps: %i. SPS: %f" % (episodes, steps, sps))

        episodes += 1
        mean_sps += (sps - mean_sps) / episodes

        start_time = timeit.default_timer()

        steps = 0
        mean_reward = 0.0

        if episodes == cfg.ngames:
            break
        env.reset()
    env.close()

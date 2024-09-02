from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.create_env import create_env
from nle_code_wrapper.utils.attr_dict import AttrDict


def play(cfg):
    render_mode = "human"
    if cfg.no_render:
        render_mode = None

    env = create_env(
        cfg.env, cfg=cfg, env_config=AttrDict(worker_index=0, vector_index=0, env_id=0), render_mode=render_mode
    )

    bot = Bot(env, cfg)

    obs = env.reset()

    steps = 0
    episodes = 0
    reward = 0.0
    action = None

    mean_reward = 0.0

    while True:
        action = bot.act(obs)
        if action is None:
            break

        obs, reward, done, info = env.step(action)
        steps += 1

        mean_reward += (reward - mean_reward) / steps

        if not done:
            continue

        episodes += 1

        steps = 0
        mean_reward = 0.0

        if episodes == cfg.ngames:
            break
        env.reset()

    env.close()

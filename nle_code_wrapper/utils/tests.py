from nle_utils.envs.create_env import create_env
from nle_utils.utils.attr_dict import AttrDict

from nle_code_wrapper.bot.bot import Bot


def create_bot(cfg):
    render_mode = "human"
    if cfg.no_render:
        render_mode = None

    env = create_env(
        cfg.env,
        cfg=cfg,
        env_config=AttrDict(worker_index=0, vector_index=0, env_id=0),
        render_mode=render_mode,
    )
    bot = Bot(env)

    return bot

import random
from functools import partial

import numpy as np
import pytest
from nle.nethack import actions as A
from nle_utils.envs.create_env import create_env
from nle_utils.glyph import G
from nle_utils.play import play
from nle_utils.utils.attr_dict import AttrDict

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.strategies import goto_closest_room
from nle_code_wrapper.envs.custom.play_custom import parse_custom_args
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import room_detection, save_boolean_array_pillow


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


@pytest.mark.usefixtures("register_components")
class TestGoTo(object):
    @pytest.mark.parametrize("env", ["CustomMiniHack-Premapped-Corridor-R3-v0"])
    @pytest.mark.parametrize("seed", [1])
    def test_goto_closest_room(self, env, seed):
        """
        This tests checks if we were able to go to the closest room,
        we delibrately stard with Premapped Environment so we can be sure that the room labeling will be the same
        and that multiple rooms will be visible from the start

        Note: with different seed it's possible that closest room will not be reachable!
        This will result in BotPanic and this is by design.
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--code_wrapper=False", "--no-render"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        starting_room = room_detection(bot)[0][bot.entity.position]
        goto_closest_room(bot)
        current_room = room_detection(bot)[0][bot.entity.position]

        assert starting_room != current_room

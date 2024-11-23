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
from nle_code_wrapper.bot.strategies import (
    explore_corridor,
    goto_closest_corridor,
    goto_closest_room,
    goto_closest_staircase_down,
    goto_closest_staircase_up,
    goto_closest_unexplored_room,
)
from nle_code_wrapper.bot.strategies.goto import goto_closest_room_direction
from nle_code_wrapper.envs.custom.play_custom import parse_custom_args
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import (
    corridor_detection,
    label_dungeon_features,
    room_detection,
    save_boolean_array_pillow,
)


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

        Note: for different seed this can fail.
        TODO: save map, create mock for bot, this will robustify tests
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--code_wrapper=False", "--no-render"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        starting_room = room_detection(bot)[0][bot.entity.position]
        goto_closest_room(bot)
        current_room = room_detection(bot)[0][bot.entity.position]

        assert starting_room != current_room

    @pytest.mark.parametrize("env", ["CustomMiniHack-Premapped-Corridor-R5-v0"])
    @pytest.mark.parametrize("compass,seed", [("east", 1), ("west", 1), ("north", 4), ("south", 1)])
    def test_goto_closest_room_direction(self, env, seed, compass):
        """
        This tests checks if we were able to go to the closest unexplored room,
        we delibrately stard with Premapped Environment so we can be sure that the room labeling will be the same
        and that multiple rooms will be visible from the start

        Note: for different seed this can fail.
        TODO: save map, create mock for bot, this will robustify tests
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--code_wrapper=False", "--no-render"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        position = bot.entity.position
        goto_closest_room_direction(bot, compass)
        new_position = bot.entity.position
        if compass == "east":
            assert new_position[1] > position[1]
        elif compass == "west":
            assert new_position[1] < position[1]
        elif compass == "north":
            assert new_position[0] < position[0]
        elif compass == "south":
            assert new_position[0] > position[0]

    @pytest.mark.parametrize("env", ["CustomMiniHack-Premapped-Corridor-R3-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_goto_closest_unexplored_room(self, env, seed):
        """
        This tests checks if we were able to go to the closest unexplored room,
        we delibrately stard with Premapped Environment so we can be sure that the room labeling will be the same
        and that multiple rooms will be visible from the start

        Note: for different seed this can fail.
        TODO: save map, create mock for bot, this will robustify tests
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--code_wrapper=False", "--no-render"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        # there are 3 rooms, for this seed all should be reachable
        # we have 2 rooms to explore, thrid call should do nothing and return False
        assert goto_closest_unexplored_room(bot)
        assert goto_closest_unexplored_room(bot)
        assert not goto_closest_unexplored_room(bot)

    @pytest.mark.parametrize("env", ["CustomMiniHack-Premapped-Corridor-R3-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_goto_closest_staricase_up(self, env, seed):
        """
        This tests checks if we were able to go to the closest unexplored room,
        we delibrately stard with Premapped Environment so we can be sure that the room labeling will be the same
        and that multiple rooms will be visible from the start

        Note: for different seed this can fail.
        TODO: save map, create mock for bot, this will robustify tests
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--code_wrapper=False", "--no-render"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        goto_closest_unexplored_room(bot)
        staircase = utils.isin(bot.current_level.objects, G.STAIR_UP)
        staircase_position = np.argwhere(staircase)
        goto_closest_staircase_up(bot)
        assert np.all(staircase_position == bot.entity.position)

import numpy as np
import pytest
from nle_utils.glyph import G

from nle_code_wrapper.bot.strategies import goto_room, goto_unexplored_room, goto_upstairs
from nle_code_wrapper.bot.strategies.goto import goto_feature_direction
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import (
    corridor_detection,
    label_dungeon_features,
    room_detection,
    save_boolean_array_pillow,
)
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestGoTo(object):
    @pytest.mark.parametrize("env", ["CustomMiniHack-Premapped-Corridor-R3-v0"])
    @pytest.mark.parametrize("seed", [1])
    def test_goto_room(self, env, seed):
        """
        This tests checks if we were able to go to the closest room,
        we delibrately stard with Premapped Environment so we can be sure that the room labeling will be the same
        and that multiple rooms will be visible from the start
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--code_wrapper=False",
                "--no-render",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        starting_room = room_detection(bot)[0][bot.entity.position]
        goto_room(bot)
        current_room = room_detection(bot)[0][bot.entity.position]

        assert starting_room != current_room

    @pytest.mark.parametrize("env", ["CustomMiniHack-Premapped-Corridor-R5-v0"])
    @pytest.mark.parametrize("compass,seed", [("east", 1), ("west", 1), ("north", 4), ("south", 1)])
    def test_goto_room_direction(self, env, seed, compass):
        """
        check if we can go to the closest room in a specific direction
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--code_wrapper=False",
                "--no-render",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        position = bot.entity.position
        goto_feature_direction(bot, compass, room_detection)
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
    def test_goto_unexplored_room(self, env, seed):
        """
        check if we can go to the closest unexplored room,
        also check if we stop exploring when we visited all rooms
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--code_wrapper=False",
                "--no-render",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        # there are 3 rooms, for this seed all should be reachable
        # we have 2 rooms to explore, thrid call should do nothing and return False
        assert goto_unexplored_room(bot)
        assert goto_unexplored_room(bot)
        assert not goto_unexplored_room(bot)

    @pytest.mark.parametrize("env", ["CustomMiniHack-Premapped-Corridor-R3-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_goto_staricase_up(self, env, seed):
        """
        check if we can go to the closest staircase up
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--code_wrapper=False",
                "--no-render",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        goto_unexplored_room(bot)
        staircase = utils.isin(bot.current_level.objects, G.STAIR_UP)
        staircase_position = np.argwhere(staircase)
        goto_upstairs(bot)
        assert np.all(staircase_position == bot.entity.position)

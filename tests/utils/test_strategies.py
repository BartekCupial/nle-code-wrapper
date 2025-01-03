import pytest

from nle_code_wrapper.bot.strategies import explore_corridor_systematically, goto_corridor, goto_room, open_doors
from nle_code_wrapper.envs.custom.play_custom import parse_custom_args
from nle_code_wrapper.utils import utils
from nle_code_wrapper.utils.strategies import corridor_detection
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestFeatures(object):
    @pytest.mark.parametrize("env", ["CustomMiniHack-Premapped-Corridor-R5-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_corridor_detection(self, env, seed):
        """
        check if corridors are detected correctly:
        """
        cfg = parse_custom_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--code_wrapper=False",
                "--no-render",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        room_position = bot.entity.position

        # - when we are in doors
        goto_corridor(bot)
        labeled_corridors, num_corridors = corridor_detection(bot)
        door_position = bot.entity.position
        assert labeled_corridors[door_position] != 0
        assert labeled_corridors[room_position] == 0

        # - when we are in corridor
        explore_corridor_systematically(bot)
        labeled_corridors, num_corridors = corridor_detection(bot)
        corridor_position = bot.entity.position
        assert labeled_corridors[door_position] != 0
        assert labeled_corridors[corridor_position] != 0
        assert labeled_corridors[room_position] == 0

        # - when we are in room
        open_doors(bot)
        goto_room(bot)
        labeled_corridors, num_corridors = corridor_detection(bot)
        assert labeled_corridors[door_position] != 0
        assert labeled_corridors[corridor_position] != 0
        assert labeled_corridors[room_position] == 0

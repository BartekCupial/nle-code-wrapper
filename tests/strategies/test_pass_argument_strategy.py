import pytest
from nle_utils.play import play

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.bot.exceptions import BotFinished
from nle_code_wrapper.bot.strategies import goto
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize("env", ["MiniHack-Room-5x5-v0"])
    @pytest.mark.parametrize("seed", [0])
    def test_pass_argument_strategy(self, env, seed):
        cfg = parse_minihack_args(argv=[f"--env={env}", f"--seed={seed}", "--code_wrapper=True", "--no-render"])

        def get_action(env, mode, obs, var=[0]):
            cur_pos = env.bot.entity.position
            distances = env.bot.pathfinder.distances(cur_pos)
            furthest = max(distances.items(), key=lambda s: s[1])[0]

            if var[0] == 0:
                ret = 0
            elif var[0] == 1:
                ret = furthest[0]
            elif var[0] == 2:
                ret = furthest[1]
            else:
                raise BotFinished

            var[0] += 1
            return ret

        cfg.strategies = [goto]
        with pytest.raises(BotFinished):
            play(cfg, get_action=get_action)

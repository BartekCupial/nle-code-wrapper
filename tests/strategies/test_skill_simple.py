import pytest
from nle.nethack import actions as A

from nle_code_wrapper.bot.exceptions import BotFinished
from nle_code_wrapper.bot.strategies.pickup import pickup_closest_boots, pickup_closest_potion, pickup_closest_ring
from nle_code_wrapper.bot.strategies.skill_simple import puton_ring, quaff_potion, wear_boots
from nle_code_wrapper.envs.custom.play_custom import parse_custom_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestSkillSimple:
    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-WearBoots-Fixed-v0"),
            ("CustomMiniHack-WearBoots-Distr-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_wear_boots(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_closest_boots(bot)
        with pytest.raises(BotFinished):
            wear_boots(bot)

    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-PutOnRing-Fixed-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_puton_ring(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_closest_ring(bot)
        with pytest.raises(BotFinished):
            puton_ring(bot)

    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-QuaffPotion-Fixed-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_quaff_potion(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_closest_potion(bot)
        with pytest.raises(BotFinished):
            quaff_potion(bot)

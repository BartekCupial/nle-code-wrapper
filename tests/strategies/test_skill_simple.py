import pytest
from nle.nethack import actions as A

from nle_code_wrapper.bot.exceptions import BotFinished
from nle_code_wrapper.bot.strategies import (
    pickup_armor,
    pickup_potion,
    pickup_ring,
    puton_ring,
    quaff_potion,
    wear_boots,
    wear_cloak,
    wear_shirt,
    wear_suit,
)
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
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
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_armor(bot)
        pickup_armor(bot)
        with pytest.raises(BotFinished):
            wear_boots(bot)

    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-WearSuit-Fixed-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_wear_one(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_armor(bot)
        assert wear_suit(bot)

    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-WearSuit-Distr-v0"),
            ("CustomMiniHack-WearSuit-Pile-v0"),
            ("CustomMiniHack-WearSuit-HugePile-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_wear_multiple(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        while pickup_armor(bot):
            pass
        assert wear_boots(bot)
        assert wear_cloak(bot)
        assert wear_suit(bot)
        assert wear_shirt(bot)

    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-WearSuit-Pile-v0"),
            ("CustomMiniHack-WearSuit-HugePile-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_pickup_pile(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_armor(bot)
        assert wear_boots(bot)
        assert wear_cloak(bot)
        assert wear_suit(bot)
        assert wear_shirt(bot)

    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-WearSuit-HugePile-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_pickup_later(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                # "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_potion(bot)
        assert len(bot.inventory["potions"]) >= 1

    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-WearSuit-CloakPile-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_pickup_more(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_armor(bot)
        assert len(bot.inventory["armor"]) >= 20

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
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_ring(bot)
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
        cfg = parse_minihack_args(
            argv=[
                f"--env={env}",
                f"--seed={seed}",
                "--no-render",
                "--code_wrapper=False",
            ]
        )
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_potion(bot)
        with pytest.raises(BotFinished):
            quaff_potion(bot)

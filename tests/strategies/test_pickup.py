import pytest
from nle.nethack import actions as A

from nle_code_wrapper.bot.exceptions import BotFinished
from nle_code_wrapper.bot.strategies.pickup import pickup_boots, pickup_horn, pickup_ring, pickup_wand
from nle_code_wrapper.envs.custom.play_custom import parse_custom_args
from nle_code_wrapper.utils.tests import create_bot


@pytest.mark.usefixtures("register_components")
class TestPickUp(object):
    @pytest.mark.parametrize(
        "env, fn, key",
        [
            ("CustomMiniHack-ZapWand-Fixed-v0", pickup_wand, "wands"),
            ("CustomMiniHack-PutOnRing-Fixed-v0", pickup_ring, "rings"),
            ("CustomMiniHack-ApplyHorn-Fixed-v0", pickup_horn, "tools"),
            ("CustomMiniHack-WearBoots-Fixed-v0", pickup_boots, "armor"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_pickup_item(self, env, fn, key, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        starting = len(bot.inventory[key])
        fn(bot)
        current = len(bot.inventory[key])

        assert starting < current

    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-WearBoots-Fixed-v0"),
            ("CustomMiniHack-WearBoots-Distr-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_pickup_boots(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_boots(bot)

        def wear_boots(bot):
            items = bot.inventory["armor"]
            for item in items:
                if "boots" in item.name:
                    bot.step(A.Command.WEAR)
                    bot.step(item.letter)

        with pytest.raises(BotFinished):
            wear_boots(bot)

    @pytest.mark.parametrize(
        "env",
        [
            ("CustomMiniHack-ApplyHorn-Fixed-v0"),
            ("CustomMiniHack-ApplyHorn-Distr-v0"),
        ],
    )
    @pytest.mark.parametrize("seed", [0])
    def test_pickup_horn(self, env, seed):
        """
        This tests checks if we were able to pick up the closest item of type
        """
        cfg = parse_custom_args(argv=[f"--env={env}", f"--seed={seed}", "--no-render", "--code_wrapper=False"])
        bot = create_bot(cfg)
        bot.reset(seed=seed)

        pickup_horn(bot)

        def use_horn(bot):
            items = bot.inventory["tools"]
            for item in items:
                if "horn" in item.name:
                    bot.step(A.Command.APPLY)
                    bot.step(item.letter)
                    if "Improvise?" in bot.message:
                        bot.type_text("y")
                        if "In what direction?" in bot.message:
                            bot.step(A.CompassCardinalDirection.S)
                            raise BotFinished

        with pytest.raises(BotFinished):
            use_horn(bot)

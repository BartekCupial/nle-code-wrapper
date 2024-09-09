import pytest
from nle_utils.glyph import G

from nle_code_wrapper.bot.bot import Bot
from nle_code_wrapper.envs.minihack.play_minihack import parse_minihack_args
from nle_code_wrapper.plugins.strategy import Strategy
from nle_code_wrapper.utils import utils


@pytest.mark.usefixtures("register_components")
class TestMazewalkMapped(object):
    @pytest.mark.parametrize("env", ["mini_eat"])
    def test_mini_eat(self, env):
        cfg = parse_minihack_args(argv=[f"--env={env}"])
        bot = Bot(cfg)

        @Strategy.wrap
        def eat(bot: "Bot"):
            bot.eat()
            while "; eat it? [ynq]" in bot.message or "; eat one? [ynq]" in bot.message:
                if "here; eat it? [ynq]" in bot.message or "here; eat one? [ynq]" in bot.message:
                    bot.type_text("y")
                    yield True
            yield False

        @Strategy.wrap
        def goto_food(bot: "Bot"):
            food_coords = utils.coords(bot.glyphs, G.FOOD_OBJECTS)
            distances = bot.pathfinder.distances(bot.entity.position)

            food = min(
                (e for e in food_coords if e in distances),
                key=lambda e: distances[e],
                default=None,
            )

            if food:
                bot.pathfinder.goto(food)
                yield True
            else:
                yield False

        bot.strategy(goto_food)
        bot.strategy(eat)

        status = bot.main()
        assert status == bot.env.StepStatus.TASK_SUCCESSFUL

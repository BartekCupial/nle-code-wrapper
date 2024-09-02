from nle_code_wrapper.bot.strategy_selector import select_strategy
from nle_code_wrapper.game_context.game_context import GameContext


class Bot:
    def __init__(self, env, cfg):
        self.env = env
        self.cfg = cfg

    def act(self, obs):
        game_context = GameContext(self.env, obs)
        strategy = select_strategy(game_context)
        return strategy(game_context)

from collections import defaultdict

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.exceptions import EnemyAppeared


def enemy_appeared(bot: "Bot"):
    last_entities = defaultdict(int)
    current_entities = defaultdict(int)

    # Count entities from current observation
    for entity in bot.entities:
        if bot.pathfinder.get_path_to(entity.position):
            current_entities[entity.glyph] += 1

    # Count entities from previous observation
    for entity in bot.get_entities(bot.last_obs):
        if bot.pathfinder.get_path_to(entity.position):
            last_entities[entity.glyph] += 1

    # Check for new enemies by comparing counts
    for glyph, count in current_entities.items():
        # If there are more entities of this type now than before
        if count > last_entities[glyph]:
            # raise Panic if new enemies appeared
            raise EnemyAppeared

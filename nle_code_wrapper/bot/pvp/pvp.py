from typing import TYPE_CHECKING

from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.exceptions import EnemyAppeared

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


class Pvp:
    def __init__(self, bot: "Bot"):
        self.bot = bot

        # The current target entity
        self.target: Entity = None

        self.movements = bot.movements

        # How far away the target entity must be to lose the target.
        # Target entities further than this distance from the bot will be considered defeated.
        self.view_distance = 10

        # How close the bot must be to the target entity to attack it.
        self.attack_range = 1

    def update(self):
        # Updates the bot's target.
        # If the target entity is defeated, the bot will stop attacking it.
        # If the target entity is out of range, the bot will stop attacking it.
        # If the target entity is not in the bot's line of sight, the bot will stop attacking it.
        if self.target:
            pathfinder = self.bot.pathfinder

            last_score = self.bot.get_blstats(self.bot.last_obs).score
            current_score = self.bot.blstats.score
            # for each monster kill, we get 4 times the difficulty in score
            if current_score - last_score == self.target.difficulty * 4:
                self.target = None
                return

            entities = [entity for entity in self.bot.entities if entity.glyph == self.target.glyph]
            closest_entity = min(
                entities,
                key=lambda entity: pathfinder.distance(self.bot.entity.position, entity.position),
                default=None,
            )
            if closest_entity:
                self.target = (
                    closest_entity
                    if pathfinder.distance(self.bot.entity.position, self.target.position) <= self.view_distance
                    else None
                )
            else:
                self.target = None

    def attack(self, entity: Entity):
        # Causes the bot to begin attacking an entity until it is killed or told to stop.
        self.target = entity
        pathfinder = self.bot.pathfinder

        try:
            while self.target:
                if pathfinder.distance(self.bot.entity.position, self.target.position) > self.attack_range:
                    path = pathfinder.get_path_to(self.target.position)
                    if path:
                        pathfinder.move(path[1])
                else:
                    self.attempt_attack()
        # TODO: think if this always help
        except EnemyAppeared:
            pass

    def attempt_attack(self):
        # TODO: implement stuff like wielding weapons if needed
        if self.target:
            self.bot.pathfinder.direction(self.target.position)

import itertools
from typing import TYPE_CHECKING

import numpy as np
from nle.nethack import actions as A

from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.exceptions import EnemyAppeared
from nle_code_wrapper.bot.pvp.ray import RaySimulator

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


class Pvp:
    def __init__(self, bot: "Bot"):
        self.bot = bot

        # The current target entity
        self.target: Entity = None

        self.movements = bot.movements
        self.ray_simulator = RaySimulator(bot)

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
                self.target = closest_entity
            else:
                self.target = None

    def attack_melee(self, entity: Entity):
        self.target = entity
        pathfinder = self.bot.pathfinder

        try:
            # attack an entity until it is killed or told to stop.
            while self.target:
                path = pathfinder.get_path_from_to(self.bot.entity.position, self.target.position)
                if path:
                    if len(path) - 1 > self.attack_range:
                        path = pathfinder.get_path_to(self.target.position)
                        if path:
                            pathfinder.move(path[1])
                    else:
                        if self.target:
                            self.bot.pathfinder.direction(self.target.position)
                else:
                    # there is no path to the target
                    self.target = None

        # TODO: write separate strategies for single monster and multiple monsters
        # 1) when we are fighting multiple monsters, we want to keep fighting
        # 2) when we are fighting one monster and another monster appears, we want to stop fighting
        except EnemyAppeared:
            pass
        except Exception as e:
            self.target = None
            raise e

    def zap_wand(self, entity: Entity):
        self.target = entity
        pathfinder = self.bot.pathfinder

        while self.target:
            # 1) check if there is a ray that can hit the target
            ray_simulations = []
            for i, j in itertools.product([-1, 0, 1], repeat=2):
                if i == 0 and j == 0:
                    continue
                hit_targets = self.ray_simulator.simulate_ray(self.bot.entity.position, (i, j))
                ray_simulations.append((hit_targets, (i, j)))
            ray_simulations = sorted(
                ray_simulations,
                key=lambda x: (
                    x[0][self.target.position],  # Maximize target damage
                    -x[0][self.bot.entity.position],  # Minimize self damage
                ),
                reverse=True,
            )

            best_ray = ray_simulations[0][1]
            best_hit = ray_simulations[0][0][self.target.position]
            self_hit = ray_simulations[0][0][self.bot.entity.position]

            # 2) if there is a ray, zap the wand
            if best_hit > 0.8 and self_hit < 0.2:
                wand = self.find_best_offensive_wand()
                if wand:
                    self.bot.step(A.Command.ZAP)
                    self.bot.step(wand.letter)
                    self.bot.pathfinder.direction(np.array(self.bot.entity.position) + best_ray)
                    return True
                else:
                    return False
            else:
                # 3) if there is no ray, move towards the target
                path = pathfinder.get_path_to(self.target.position)
                if path:
                    pathfinder.move(path[1])
                else:
                    self.target = None

    def find_best_offensive_wand(self):
        items = self.bot.inventory["wands"]

        # First try wands of death, then cold, then any other wands
        wand_priorities = [
            lambda item: "wand of death" in item.full_name,
            lambda item: "wand of cold" in item.full_name,
            lambda item: True,
        ]

        for priority_check in wand_priorities:
            for item in items:
                if priority_check(item):
                    return item

        return None

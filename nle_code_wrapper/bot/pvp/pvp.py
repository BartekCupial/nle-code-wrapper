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
        self.melee_range = 1

    def update(self):
        # Updates the bot's target.
        # If the target entity is defeated, the bot will stop attacking it.
        # If the target entity is out of range, the bot will stop attacking it.
        # If the target entity is not in the bot's line of sight, the bot will stop attacking it.
        if self.target:
            pathfinder = self.bot.pathfinder

            # TODO: this is faulty, because we could kill more monsters then one (e.g. with a wand of death)
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

    def approach_target(self, target_position, desired_range: int = 1):
        """Common logic for approaching a target"""
        path = self.bot.pathfinder.get_path_to(target_position)
        if not path:
            return False

        if len(path) - 1 > desired_range:
            self.bot.pathfinder.move(path[1])
            return True
        return False

    def handle_combat(self, entity: Entity, action_func):
        """Template method for combat actions"""
        self.target = entity

        try:
            while self.target:
                if not action_func():
                    self.target = None

        except EnemyAppeared:
            pass
        except Exception as e:
            self.target = None
            raise e

    def approach_entity(self, entity: Entity, distance: int = 1):
        def approach_action():
            return self.approach_target(self.target.position, distance)

        self.handle_combat(entity, approach_action)

    def attack_melee(self, entity: Entity):
        # TODO: write separate strategies for single monster and multiple monsters
        # 1) when we are fighting multiple monsters, we want to keep fighting
        # 2) when we are fighting one monster and another monster appears, we want to stop fighting
        def melee_action():
            if self.approach_target(self.target.position, self.melee_range):
                return True

            # TODO: what about neutral monsters? we need to confirm attack
            self.bot.pathfinder.direction(self.target.position)
            return True

        self.handle_combat(entity, melee_action)

    def _simulate_rays(self, ray_range):
        ray_simulations = []
        for i, j in itertools.product([-1, 0, 1], repeat=2):
            if i == 0 and j == 0:
                continue
            hit_targets = self.ray_simulator.simulate_ray(self.bot.entity.position, (i, j), ray_range=ray_range)
            ray_simulations.append((hit_targets, (i, j)))

        return ray_simulations

    def _get_best_ray(self, ray_simulations):
        """Find the best ray based on target damage and self damage"""
        sorted_rays = sorted(
            ray_simulations,
            key=lambda x: (
                x[0][self.target.position],
                -x[0][self.bot.entity.position],
            ),
            reverse=True,
        )
        best = sorted_rays[0]
        return (
            best[1],  # best_ray
            best[0][self.target.position],  # target_hit
            best[0][self.bot.entity.position],  # self_hit
        )

    def _find_best_offensive_wand(self):
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

    def _execute_wand_zap(self, best_ray):
        """Execute the wand zap action"""
        wand = self._find_best_offensive_wand()
        if not wand:
            return False

        self.bot.step(A.Command.ZAP)
        self.bot.step(wand.letter)
        self.bot.pathfinder.direction(np.array(self.bot.entity.position) + best_ray)
        return True

    def zap_entity(self, entity: Entity):
        def wand_action():
            # 1) check if we have a wand
            if self._find_best_offensive_wand() is None:
                return False

            # try to be optimistic about ray_distance
            ray_simulations = self._simulate_rays(ray_range=self.ray_simulator.max_range)
            best_ray, target_hit, self_hit = self._get_best_ray(ray_simulations)

            # 3) zap the wand if criteria are met
            if target_hit > 0.8 and self_hit < 0.2:
                return self._execute_wand_zap(best_ray)
            else:
                return False

        self.handle_combat(entity, wand_action)

    def approach_and_zap_entity(self, entity: Entity):
        def wand_action():
            # 1) check if we have a wand
            if self._find_best_offensive_wand() is None:
                return False

            # 2) come in range of the target
            if self.approach_target(self.target.position, self.ray_simulator.min_range):
                return True

            # try to be optimistic about ray_distance
            ray_simulations = self._simulate_rays(ray_range=self.ray_simulator.max_range)
            best_ray, target_hit, self_hit = self._get_best_ray(ray_simulations)

            # 3) zap the wand if criteria are met
            if target_hit > 0.8 and self_hit < 0.2:
                return self._execute_wand_zap(best_ray)
            # 4) if we can't zap, try to move closer
            else:
                # 5) try to move closer
                if len(self.bot.pathfinder.get_path_to(self.target.position)) - 1 > self.melee_range:
                    return self.approach_target(self.target.position)
                # 6) we are in melee range, but we can't zap the wand (e.g. we are near a wall), abort
                else:
                    return False

        self.handle_combat(entity, wand_action)

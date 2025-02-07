import itertools
from typing import TYPE_CHECKING, List, Optional, Tuple

import numpy as np
from nle.nethack import actions as A

from nle_code_wrapper.bot.character import Role
from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.exceptions import EnemyAppeared
from nle_code_wrapper.bot.inventory import Item
from nle_code_wrapper.bot.pvp.ray import RaySimulator
from nle_code_wrapper.bot.pvp.utils import calc_dps

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


class Pvp:
    def __init__(self, bot: "Bot"):
        self.bot = bot

        # The current target entity
        self.target: Entity = None

        self.ray_simulator = RaySimulator(bot)

        # How close the bot must be to the target entity to attack it.
        self.melee_range = 1
        self.ranged_range = 7

    def update(self):
        # Updates the bot's target.
        # If the target entity is defeated, the bot will stop attacking it.
        # If the target entity is out of range, the bot will stop attacking it.
        # If the target entity is not in the bot's line of sight, the bot will stop attacking it.
        if self.target:
            pathfinder = self.bot.pathfinder

            # TODO: when should we fight monsters when we are blind?

            # if we have increased score for sure monster died
            last_score = self.bot.get_blstats(self.bot.last_obs).score
            current_score = self.bot.blstats.score
            if current_score > last_score:
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

    def approach_target(self, target: Entity, desired_range: int = 1):
        """Common logic for approaching a target"""
        if target is None:
            return True

        adjacent = self.bot.pathfinder.reachable(self.bot.entity.position, target.position, adjacent=True)
        if adjacent is None:
            return False

        path = self.bot.pathfinder.get_path_to(adjacent)

        if len(path) > desired_range:
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

                if self.bot.in_yn_function or self.bot.in_getlin:
                    self.target = None

        except EnemyAppeared:
            pass
        except Exception as e:
            self.target = None
            raise e

    def approach(self, entity: Entity, distance: int = 1):
        def approach_action():
            return self.approach_target(self.target, distance)

        self.handle_combat(entity, approach_action)

    def attack_melee(self, entity: Entity):
        def melee_action():
            self.wield_best_melee_weapon()

            if self.approach_target(self.target, self.melee_range):
                return True

            self.bot.pathfinder.direction(self.target.position)
            return True

        self.handle_combat(entity, melee_action)

    def wield_best_melee_weapon(self):
        best_melee_weapon = self.get_best_melee_weapon()
        if best_melee_weapon:
            if not best_melee_weapon.equipped:
                self.bot.step(A.Command.WIELD)
                self.bot.step(best_melee_weapon.letter)

            # we should have weapon at equipped now
            if not best_melee_weapon.equipped:
                return False

            return True
        else:
            if self.bot.character.role == Role.MONK:
                return True
            else:
                return False

    def get_best_melee_weapon(self) -> Item:
        if self.bot.character.role == Role.MONK:
            return None

        # select the best
        best_item = None
        best_dps = calc_dps(*self.bot.character.get_melee_bonus(None))
        for item in self.bot.inventory["weapons"]:
            if item.is_firing_projectile or item.is_thrown_projectile:
                continue

            to_hit, dmg = self.bot.character.get_melee_bonus(item)
            dps = calc_dps(to_hit, dmg)
            if best_dps < dps:
                best_dps = dps
                best_item = item
        return best_item

    def attack_ranged(self, entity: Entity):
        def attack_action():
            def move_attack_position(attack_positions):
                current_position = self.bot.entity.position
                if current_position in attack_positions:
                    return False  # Already in position

                # move one step closer to closest attack position
                distances = self.bot.pathfinder.distances(current_position)
                goto_position = min(
                    attack_positions,
                    key=lambda p: distances.get(p, np.inf),
                    default=None,
                )
                path = self.bot.pathfinder.get_path_to(goto_position)
                self.bot.pathfinder.move(path[1])
                return True

            def direction_to_monster() -> Optional[Tuple[int, int]]:
                p1 = self.bot.entity.position
                p2 = self.target.position

                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]

                if dx != 0:
                    dx = dx // abs(dx)
                if dy != 0:
                    dy = dy // abs(dy)

                return (p1[0] + dx, p1[1] + dy)

            # 1) Check ranged weapon and ammo
            # Control questions:
            # - what happens when you run out of ammo?
            #   wield_best_ranged_set will just return False and we are out of the strategy
            #   we could also raise BotPanic no ammo
            if not self.wield_best_ranged_set():
                return False

            # 2) Get into range
            if self.approach_target(self.target, self.ranged_range):
                return True

            # 3) Positions from we can attack
            attack_positions = self._straight_lines(self.target.position)

            # 3) Calculate distance and direction
            if move_attack_position(attack_positions):
                return True

            direction = direction_to_monster()
            if direction is None:
                return True

            # 4) Execute attack
            self.bot.step(A.Command.FIRE)
            if "In what direction?" in self.bot.message:
                self.bot.pathfinder.direction(direction)
            return True

        self.handle_combat(entity, attack_action)

    def _straight_lines(self, position):
        level = self.bot.current_level
        positions = []
        for dx, dy in itertools.product([-1, 0, 1], repeat=2):
            if dx == 0 and dy == 0:
                continue

            p = position
            while level.safe_walkable[p[0] + dx, p[1] + dy]:
                p = (p[0] + dx, p[1] + dy)
                positions.append(p)

        return positions

    def wield_best_ranged_set(self):
        best_launcher, best_ammo = self.get_best_ranged_set()
        if not best_launcher and not best_ammo:
            return False

        if best_launcher:
            if not best_launcher.equipped:
                self.bot.step(A.Command.WIELD)
                self.bot.step(best_launcher.letter)

            # we should have launcher equipped now
            if not best_launcher.equipped:
                return False

        if best_ammo:
            if not best_ammo.at_ready:
                self.bot.step(A.Command.QUIVER)
                self.bot.step(best_ammo.letter)

            # we should have ammo at ready now
            if not best_ammo.at_ready:
                return False

        return True

    def get_best_ranged_set(self) -> Tuple[Item, Item]:
        best_launcher, best_ammo, best_dps = None, None, -np.inf
        for launcher, ammo in self.get_ranged_combinations():
            dps = calc_dps(*self.bot.character.get_ranged_bonus(launcher, ammo))
            if dps > best_dps:
                best_launcher, best_ammo, best_dps = launcher, ammo, dps
        return best_launcher, best_ammo

    def get_ranged_combinations(self):
        weapons: List[Item] = self.bot.inventory["weapons"]
        launchers = [i for i in weapons if i.is_launcher]
        ammo_list = [i for i in weapons if i.is_firing_projectile]
        valid_combinations = []

        for launcher in launchers:
            for ammo in ammo_list:
                if launcher.can_shoot_projectile(ammo):
                    # TODO: handle beatitude, we dont want to use cursed launcher
                    valid_combinations.append((launcher, ammo))

        best_melee_weapon = self.get_best_melee_weapon()
        wielded_melee_weapon = self.bot.inventory.main_hand
        valid_combinations.extend(
            [
                (None, i)
                for i in weapons
                if i.is_thrown_projectile and i != best_melee_weapon and i != wielded_melee_weapon
            ]
        )

        return valid_combinations

    def _simulate_rays(self, ray_range):
        ray_simulations = []
        for i, j in itertools.product([-1, 0, 1], repeat=2):
            if i == 0 and j == 0:
                continue
            hit_targets = self.ray_simulator.simulate_ray(self.bot.entity.position, (i, j), ray_range=ray_range)
            ray_simulations.append((hit_targets, (i, j)))

        return ray_simulations

    def _get_best_ray(self):
        """Find the best ray based on target damage and self damage"""
        # be pessimisic for target hit and optimistic for self hit
        max_simulations = self._simulate_rays(ray_range=self.ray_simulator.max_range)
        min_simulations = self._simulate_rays(ray_range=self.ray_simulator.min_range)
        # update self hits to be optimistic, leave rest pessimistic
        for i in range(len(max_simulations)):
            min_simulations[i][0][self.bot.entity.position] = max_simulations[i][0][self.bot.entity.position]

        sorted_rays = sorted(
            min_simulations,
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
            lambda item: "wand of death" in item.name,
            lambda item: "wand of cold" in item.name,
            lambda item: "wand of striking" in item.name,
            lambda item: "wand of fire" in item.name,
            lambda item: "wand of lightning" in item.name,
            lambda item: "wand of sleep" in item.name,
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

    def zap(self, entity: Entity):
        def wand_action():
            # 1) check if we have a wand
            if self._find_best_offensive_wand() is None:
                return False

            best_ray, target_hit, self_hit = self._get_best_ray()

            # 3) zap the wand if criteria are met
            if target_hit > 0.8 and self_hit < 0.2:
                return self._execute_wand_zap(best_ray)
            else:
                return False

        self.handle_combat(entity, wand_action)

    def approach_and_zap(self, entity: Entity):
        def wand_action():
            # 1) check if we have a wand
            if self._find_best_offensive_wand() is None:
                return False

            # 2) come in range of the target
            if self.approach_target(self.target, self.ray_simulator.min_range):
                return True

            best_ray, target_hit, self_hit = self._get_best_ray()

            # 3) zap the wand if criteria are met
            if target_hit > 0.8 and self_hit < 0.2:
                return self._execute_wand_zap(best_ray)
            # 4) if we can't zap, try to move closer
            else:
                # 5) try to move closer
                adjacent = self.bot.pathfinder.reachable(self.bot.entity.position, self.target.position, adjacent=True)
                if adjacent is None:
                    return False

                path = self.bot.pathfinder.get_path_to(adjacent)
                if len(path) > self.melee_range:
                    return self.approach_target(self.target)
                # 6) we are in melee range, but we can't zap the wand (e.g. we are near a wall), abort
                else:
                    return False

        self.handle_combat(entity, wand_action)

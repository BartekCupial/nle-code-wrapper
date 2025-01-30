from collections import defaultdict
from typing import TYPE_CHECKING, Tuple

from nle_code_wrapper.utils.strategies import room_detection, save_boolean_array_pillow

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


class RaySimulator:
    def __init__(self, bot: "Bot", min_range: int = 7, max_range: int = 13):
        self.bot = bot
        self.min_range = min_range
        self.max_range = max_range

    def simulate_ray(self, start_pos: Tuple[int, int], direction: Tuple[int, int], ray_range: int = 7):
        hit_targets = defaultdict(float)
        self._simulate_ray(hit_targets, start_pos, direction, ray_range, probability=1.0)

        return hit_targets

    def _simulate_ray(
        self,
        hit_targets,
        start_pos: Tuple[int, int],
        direction: Tuple[int, int],
        remaining_range: int,
        probability: float,
    ):
        x, y = start_pos
        dx, dy = direction

        while remaining_range > 0:
            x += dx
            y += dy

            # Add bounds check
            if not self._is_in_bounds(x, y):
                return

            if self.bot.current_level.walkable[x, y]:
                for entity in self.bot.entities + [self.bot.entity]:
                    if entity.position == (x, y):
                        remaining_range -= 2
                        hit_targets[(entity.position)] += probability
            else:
                if self._is_convex_corner(dx, dy, x - dx, y - dy):
                    # the ray reflects randomly between 3 cases
                    # it has 1/20 chance of reflecting straight back
                    newdx, newdy = self._straight_bounce(dx, dy)
                    self._simulate_ray(hit_targets, (x, y), (newdx, newdy), remaining_range - 1, probability * 1 / 20)

                    # 19/40 chance of reflecting left
                    newdx, newdy = self._bounce_left(dx, dy)
                    self._simulate_ray(hit_targets, (x, y), (newdx, newdy), remaining_range - 1, probability * 19 / 40)

                    # 19/40 chance of reflecting right
                    newdx, newdy = self._bounce_right(dx, dy)
                    self._simulate_ray(hit_targets, (x, y), (newdx, newdy), remaining_range - 1, probability * 19 / 40)
                elif self._is_concave_corner(dx, dy, x - dx, y - dy):
                    newdx, newdy = self._straight_bounce(dx, dy)
                    self._simulate_ray(hit_targets, (x, y), (newdx, newdy), remaining_range - 1, probability)
                else:
                    # if moving horizontally or vertically
                    if (dx != 0 and dy == 0) or (dx == 0 and dy != 0):
                        # A ray hitting a wall straight on will move one square into the wall and then bounce straight back
                        newdx, newdy = self._straight_bounce(dx, dy)
                        self._simulate_ray(hit_targets, (x, y), (newdx, newdy), remaining_range - 1, probability)

                    # if moving diagonally
                    elif dx != 0 and dy != 0:
                        # If a ray hits a wall at an angle, it usually penetrates the wall one square and reflects accordingly.
                        newdx, newdy = self._angled_bounce(dx, dy, x - dx, y - dy)
                        self._simulate_ray(
                            hit_targets, (x, y), (newdx, newdy), remaining_range - 1, probability * 19 / 20
                        )

                        # 1/20 of the time, the ray will instead bounce straight back in the direction it came from.
                        newdx, newdy = self._straight_bounce(dx, dy)
                        self._simulate_ray(
                            hit_targets, (x, y), (newdx, newdy), remaining_range - 1, probability * 1 / 20
                        )
                    else:
                        raise ValueError()

                # if we encountered a wall stop current ray, we spawned new rays
                return

            remaining_range -= 1

    def _is_convex_corner(self, dx: int, dy: int, x: int, y: int) -> bool:
        #     ┌----
        #     |..a.
        #     |....
        #     |....
        # ┌---┘....
        # |....\...
        # |.....\..
        # |b.....@.
        # Ray heading
        # up-left

        # Check if all accessed positions are in bounds
        if not all(self._is_in_bounds(px, py) for px, py in [(x, y), (x + dx, y), (x, y + dy), (x + dx, y + dy)]):
            return False

        return (
            self.bot.current_level.walkable[x, y]
            and self.bot.current_level.walkable[x + dx, y]
            and self.bot.current_level.walkable[x, y + dy]
            and not self.bot.current_level.walkable[x + dx, y + dy]
        )

    def _is_concave_corner(self, dx: int, dy: int, x: int, y: int) -> bool:
        # ┌----
        # |\...
        # |.\..
        # |..@.
        # Ray heading
        # up-left

        # Check if all accessed positions are in bounds
        if not all(self._is_in_bounds(px, py) for px, py in [(x, y), (x + dx, y), (x, y + dy), (x + dx, y + dy)]):
            return False

        return (
            self.bot.current_level.walkable[x, y]
            and not self.bot.current_level.walkable[x + dx, y]
            and not self.bot.current_level.walkable[x, y + dy]
            and not self.bot.current_level.walkable[x + dx, y + dy]
        )

    def _straight_bounce(self, dx: int, dy: int) -> Tuple[int, int]:
        # straight bounce
        # |......
        # |<--@..
        # |......
        # Initial ray
        # direction

        return (-dx, -dy)

    def _bounce_left(self, dx: int, dy: int) -> Tuple[int, int]:
        return (-dx, dy)

    def _bounce_right(self, dx: int, dy: int) -> Tuple[int, int]:
        return (dx, -dy)

    def _angled_bounce(self, dx: int, dy: int, x: int, y: int) -> Tuple[int, int]:
        # angled bounce
        # |......
        # |..c...
        # |......
        # |b.....
        # |a.....
        # |\.....
        # |.\....
        # |..@...
        # Ray heading
        # up-left

        # if hitting a vertical wall
        if self.bot.current_level.walkable[x + dx, y]:
            return dx, -dy

        # if hitting a horizontal wall
        if self.bot.current_level.walkable[x, y + dy]:
            return -dx, dy

        raise ValueError()

    def _is_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.bot.current_level.walkable.shape[0] and 0 <= y < self.bot.current_level.walkable.shape[1]

from typing import TYPE_CHECKING

from nle_code_wrapper.bot.entity import Entity
from nle_code_wrapper.bot.exceptions import BotPanic
from nle_code_wrapper.plugins.pathfinder.goto import calc_direction, direction, move

if TYPE_CHECKING:
    from nle_code_wrapper.bot.bot import Bot


def hit(bot: "Bot", entity):
    y, x = entity.position
    dir = calc_direction(bot.blstats.y, bot.blstats.x, y, x)
    direction(bot, dir)


def attack(bot: "Bot", entity: Entity):
    path = bot.pathfinder.get_path_to(entity.position)
    orig_path = list(path)
    path = orig_path[1:]

    for y, x in path:
        try:
            if bot.pathfinder.distance(bot.entity.position, entity.position) > 1:
                move(bot, y, x)
            else:
                hit(bot, entity)
        except BotPanic:
            return False

        # if the enemy is not at original position stop attacking
        # either enemy is dead or it moved
        if len([e for e in bot.entities if e.position == entity.position and e.name == entity.name]) == 0:
            return

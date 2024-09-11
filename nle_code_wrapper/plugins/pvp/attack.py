from typing import TYPE_CHECKING

from nle_code_wrapper.bot.entity import Entity

if TYPE_CHECKING:
    from nle_code_wrapper.bot.bot import Bot


def attack(bot: "Bot", entity: Entity):
    path = bot.pathfinder.get_path_to(entity.position)
    orig_path = list(path)
    path = orig_path[1:]

    for point in path:
        if bot.pathfinder.distance(bot.entity.position, entity.position) > 1:
            bot.pathfinder.move(point)
        else:
            bot.pathfinder.direction(entity.position)

        # if the enemy is not at original position stop attacking
        # either enemy is dead or it moved
        if len([e for e in bot.entities if e.position == entity.position and e.name == entity.name]) == 0:
            return

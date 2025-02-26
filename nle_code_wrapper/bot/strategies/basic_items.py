from nle.nethack.actions import Command

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def apply(bot: "Bot"):
    """
    Execute a single 'apply' command (a).
    Tip:
    - generally used with some form of tool
    """
    bot.step(Command.APPLY)


@strategy
def dip(bot: "Bot"):
    """
    Execute a single 'dip' command (#dip).
    Tip:
    - used to dip one object into another
    """
    bot.step(Command.DIP)


@strategy
def drop(bot: "Bot"):
    """
    Execute a single 'drop' command (d).
    Tip:
    - used to remove something from your inventory
    """
    bot.step(Command.DROP)


@strategy
def eat(bot: "Bot"):
    """
    Execute a single 'eat' command (e).
    Tip:
    - replenish food when hungry
    """
    bot.step(Command.EAT)


@strategy
def engrave(bot: "Bot"):
    """
    Execute a single 'engrave' command (E).
    Tip:
    - in emergency write the name Elbereth
    """
    bot.step(Command.ENGRAVE)


@strategy
def fire(bot: "Bot"):
    """
    Execute a single 'fire' command (f).
    Tip:
    - put ammunition in quiver first
    """
    bot.step(Command.FIRE)


@strategy
def loot(bot: "Bot"):
    """
    Execute a single 'loot' command (#loot).
    """
    bot.step(Command.LOOT)


@strategy
def kick(bot: "Bot"):
    """
    Execute a single 'kick' command (#kick).
    Tip:
    - useful for breaking through locked doors
    """
    bot.step(Command.KICK)


@strategy
def invoke(bot: "Bot"):
    """
    Execute a single 'invoke' command (#invoke).
    Tip:
    - useful for activating crystall balls and quest items
    """
    bot.step(Command.INVOKE)


@strategy
def pickup(bot: "Bot"):
    """
    Execute a single 'pickup' command (,).
    Tips:
    - pick up items from the dungeon floor
    - If there is only one item or stack in your square,
      you will usually pick it up without further prompting;
      otherwise you will be asked which items you want to pick up,
      where you can use menu controls to refine your selection
    """
    bot.step(Command.PICKUP)


@strategy
def put_on(bot: "Bot"):
    """
    Execute a single 'put_on' command (P).
    Tip:
    - It is used to put on amulets, rings and eyewear
    """
    bot.step(Command.PUTON)


@strategy
def quaff(bot: "Bot"):
    """
    Execute a single 'quaff' command (q).
    Tip:
    - you can quaff a potion, from a fountain or from a sink
    """
    bot.step(Command.QUAFF)


@strategy
def quiver(bot: "Bot"):
    """
    Execute a single 'quiver' command (Q).
    Tip:
    - put objects in your quiver before firing
    """
    bot.step(Command.QUIVER)


@strategy
def read(bot: "Bot"):
    """
    Execute a single 'read' command (r).
    Tip:
    - you can read the scroll or a spellbook in an inventory
    """
    bot.step(Command.READ)


@strategy
def remove(bot: "Bot"):
    """
    Execute a single 'remove' command (R).
    Tip:
    - used to remove amulets, rings and eyewear
    """
    bot.step(Command.REMOVE)


@strategy
def rub(bot: "Bot"):
    """
    Execute a single 'rub' command (#rub).
    Tips:
    - rubbing a lamp can summon a djinni
    - rubbing a gray stone is useful for identification
    """
    bot.step(Command.RUB)


@strategy
def take_off(bot: "Bot"):
    """
    Execute a single 'takeoff' command (T).
    Tip:
    - used to take off worn armor and shields
    """
    bot.step(Command.TAKEOFF)


@strategy
def throw(bot: "Bot"):
    """
    Execute a single 'throw' command (t).
    """
    bot.step(Command.THROW)


@strategy
def wear(bot: "Bot"):
    """
    Execute a single 'wear' command (W).
    Tip:
    - used to wear pieces of armor and shields
    """
    bot.step(Command.WEAR)


@strategy
def wield(bot: "Bot"):
    """
    Execute a single 'wield' command (w).
    Tips:
    - used to wield a weapon
    - to use a ranged weapon wield a launcher then 'throw' or 'fire' the ammunition
    """
    bot.step(Command.WIELD)


@strategy
def zap(bot: "Bot"):
    """
    Execute a single 'zap' command (z).
    Tip:
    - some wands act immediately (wand of wishing, wand of light) and some ask for direction (wand to striking)
    """
    bot.step(Command.ZAP)

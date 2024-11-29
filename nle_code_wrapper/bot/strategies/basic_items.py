from nle.nethack.actions import Command

from nle_code_wrapper.bot import Bot
from nle_code_wrapper.bot.strategy import strategy


@strategy
def apply(bot: "Bot"):
    bot.step(Command.APPLY)


@strategy
def dip(bot: "Bot"):
    bot.step(Command.DIP)


@strategy
def drop(bot: "Bot"):
    bot.step(Command.DROP)


@strategy
def eat(bot: "Bot"):
    bot.step(Command.EAT)


@strategy
def engrave(bot: "Bot"):
    bot.step(Command.ENGRAVE)


@strategy
def fire(bot: "Bot"):
    bot.step(Command.FIRE)


@strategy
def invoke(bot: "Bot"):
    bot.step(Command.INVOKE)


@strategy
def pickup(bot: "Bot"):
    bot.step(Command.PICKUP)


@strategy
def put_on(bot: "Bot"):
    bot.step(Command.PUTON)


@strategy
def quaff(bot: "Bot"):
    bot.step(Command.QUAFF)


@strategy
def quiver(bot: "Bot"):
    bot.step(Command.QUIVER)


@strategy
def read(bot: "Bot"):
    bot.step(Command.READ)


@strategy
def remove(bot: "Bot"):
    bot.step(Command.REMOVE)


@strategy
def rub(bot: "Bot"):
    bot.step(Command.RUB)


@strategy
def take_off(bot: "Bot"):
    bot.step(Command.TAKEOFF)


@strategy
def throw(bot: "Bot"):
    bot.step(Command.THROW)


@strategy
def wear(bot: "Bot"):
    bot.step(Command.WEAR)


@strategy
def wield(bot: "Bot"):
    bot.step(Command.WIELD)


@strategy
def zap(bot: "Bot"):
    bot.step(Command.ZAP)

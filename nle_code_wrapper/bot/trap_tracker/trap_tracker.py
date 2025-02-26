import enum
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


class TrapType(enum.Enum):
    NONE = 0
    BEARTRAP = 1
    PIT = 2
    WEB = 3
    LAVA = 4
    INFLOOR = 5
    BURIEDBALL = 6


class TrapTracker:
    def __init__(self, bot: "Bot"):
        self.bot = bot
        self.trapped = False
        self.traptype = TrapType.NONE

        # Pre-compile regex patterns for better performance
        self.spider_web = re.compile(
            r"(?:you are caught by|you lead.*into|you (?:float|stumble) into) (?:a|your) spider web"
        )
        self.bear_trap = re.compile(r"(?:a|your) bear trap closes on (?:your|.*'s) foot")
        self.pit = re.compile(
            r"you (?:fall|plunge|dive) into (?:a|your) pit|you move into an adjacent pit|you stumble over debris|you lead .* into (?:a|your) pit"
        )
        self.spiked_pit = re.compile(r"(?:you|.*) (?:land|step)s? on a set of sharp iron spikes")

    def update(self):
        last_position = self.bot.get_entity(self.bot.last_obs).position
        position = self.bot.entity.position
        message = self.bot.message.lower()

        # check if we escaped the trap
        if last_position != position:
            self.trapped = False

        # TODO: add traptypes

        # Check if any pattern matches
        self.trapped = (
            self.trapped
            or self.spider_web.search(message) is not None
            or self.bear_trap.search(message) is not None
            or self.pit.search(message) is not None
            or self.spiked_pit.search(message) is not None
        )

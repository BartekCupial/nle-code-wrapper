from typing import TYPE_CHECKING

from nle_code_wrapper.bot.inventory.inventory import Inventory

if TYPE_CHECKING:
    from nle_code_wrapper.bot import Bot


class InventoryManager:
    def __init__(self, bot: "Bot"):
        self.bot = bot

    def update(self):
        # TODO: we should add items, but handle them differently
        # when hallucinating inv_glyphs change (set glyph=None)
        # when blinded (set obj to unknown)
        if not self.bot.hallucinating and not self.bot.blinded:
            last_obs = self.bot.current_obs
            self.inventory = Inventory(
                last_obs["inv_strs"],
                last_obs["inv_letters"],
                last_obs["inv_oclasses"],
                last_obs["inv_glyphs"],
            )

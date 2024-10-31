'''
TODO: Eventually, change functionality to search to use dropdown menu/buttons

from interactions import Button, ButtonStyle, ActionRow, StringSelectMenu, StringSelectOption
import discord
from typing import List

class searchResultsView(discord.ui.View):
    def __init__(self, options: List[StringSelectOption]):
        super().__init__()
        self.converted_options = []
        for i, string in enumerate(options):
            self.converted_options.append(StringSelectOption(label=string, value=i))
        self.selected = None

    @StringSelectMenu(placeholder='Select An Option', options=self.options)
    async def selection(self, )

    @discord.ui.button(label='Select', style=discord.ButtonStyle.green)
    async def select(self, interaction: discord.Interaction, button: discord.ui.Button):


musicActionRow: List[ActionRow] = [
    ActionRow(
        
    )
]
'''

"""Copyright 2024 Mysty<evieepy@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import discord
from discord import app_commands
from discord.ext import commands

import core


class Colours(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot: core.Bot = bot

    @app_commands.command(name="colour")
    @app_commands.checks.cooldown(2, 10.0)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def colour_command(self, interaction: discord.Interaction[core.Bot], *, value: str) -> None:
        """Display information and visuals about a colour.

        Parameters
        ----------
        value: str
            The colour in hex format or as a valid integer. E.g. #FFDD00 or 0xFFDD00 or 16768256
        """
        await interaction.response.defer()
        colour: core.Colour | None = None

        try:
            colour = core.Colour.from_int(int(value))
        except ValueError:
            pass

        if not colour:
            try:
                colour = core.Colour.from_hex(value)
            except ValueError:
                await interaction.followup.send(f"Unable to parse colour `{value}`, please try again.")
                return

        view: core.ColourView = core.ColourView(colour=colour, bot=self.bot)
        await view.prepare()

        await interaction.followup.send(view=view, embed=view.embed, files=[view.image_file, view.thumb_file])


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Colours(bot))

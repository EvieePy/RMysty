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

import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import core


class Random(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot: core.Bot = bot

    @app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def countdown(self, interaction: discord.Interaction) -> None:
        """Start a countdown of 3 seconds."""
        msg = (
            "Press start when you are ready to countdown from `3`.\nThis view will only be available for `90 seconds`."
        )

        view = core.CountdownView(user_id=interaction.user.id)
        await interaction.response.send_message(msg, view=view)
        await view.wait()

        if view.result is False:
            await interaction.followup.send("Cancelling countdown!")
            return

        msg_: discord.WebhookMessage = await interaction.followup.send("\u0033\ufe0f\u20e3")  # type: ignore
        await asyncio.sleep(1)

        for i in range(2, 0, -1):
            await msg_.edit(content=f"{i}\ufe0f\u20e3")
            await asyncio.sleep(1)

        await msg_.edit(content="\ud83c\uddec \ud83c\uddf4 \u2757")


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Random(bot))

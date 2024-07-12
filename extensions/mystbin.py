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

from typing import TYPE_CHECKING, Any

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

import core


if TYPE_CHECKING:
    from types_.mystbin import BinFile


ALLOWED_INSTALL: app_commands.AppInstallationType = app_commands.AppInstallationType(user=True, guild=True)
MYSTBIN_API: str = "https://mystb.in/api/paste"
MYSTBIN_URL: str = "https://mystb.in/"


class MystBin(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot: core.Bot = bot
        self.ctxmenu: app_commands.ContextMenu = app_commands.ContextMenu(
            name="Message to MystBin",
            callback=self.convert_mystbin,
            allowed_installs=ALLOWED_INSTALL,
        )

        self.session: aiohttp.ClientSession | None = None

    async def cog_load(self) -> None:
        self.bot.tree.add_command(self.ctxmenu)
        self.session = aiohttp.ClientSession()

    async def cog_unload(self) -> None:
        if self.session:
            try:
                await self.session.close()
            finally:
                self.session = None

        self.bot.tree.remove_command(self.ctxmenu.name, type=self.ctxmenu.type)

    # @commands.hybrid_command()
    # @app_commands.allowed_installs(guilds=True, users=True)
    # async def mystbin(self, context: commands.Context[core.Bot], *, content: str) -> None: ...

    async def convert_mystbin(self, interaction: discord.Interaction[core.Bot], message: discord.Message) -> None:
        assert self.session

        await interaction.response.defer()

        parsed: core.CodeBlocks = core.CodeBlocks.convert(message.content)
        files: list[BinFile] = []

        for index, block in enumerate(parsed.blocks, 1):
            name = f"block_{index}.{block['language'] or 'txt'}"
            files.append({"filename": name, "content": block["content"]})

        if len(files) < 5:
            content: str = (
                f"{message.author}({message.author.id}) in {message.channel}({message.channel.id})\n"
                f"{message.created_at}\n\n{message.content}"
            )
            files.append({"filename": f"{message.id}.txt", "content": content})

        async with self.session.post(MYSTBIN_API, json={"files": files[:5]}) as resp:
            if resp.status != 200:
                await interaction.followup.send(f"An error occurred creating this paste: `{resp.status}`")
                return

            data: dict[str, Any] = await resp.json()
            await interaction.followup.send(f"{MYSTBIN_URL}{data['id']}")


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(MystBin(bot))

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

import datetime
from typing import TYPE_CHECKING

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

import core
from types_.mystbin import PasteFetch


if TYPE_CHECKING:
    from types_.mystbin import MBFileCreate, PasteCreateResp


ALLOWED_INSTALL: app_commands.AppInstallationType = app_commands.AppInstallationType(user=True, guild=True)
ALLOWED_CONTEXT: app_commands.AppCommandContext = app_commands.AppCommandContext(
    guild=True,
    dm_channel=True,
    private_channel=True,
)
MYSTBIN_API: str = "https://mystb.in/api/paste"
MYSTBIN_URL: str = "https://mystb.in/"


class Node:
    def __init__(self, *, identifier: str, last_edit: datetime.datetime | None) -> None:
        self.identifier: str = identifier
        self.last_edit: datetime.datetime | None = last_edit


class MystBin(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot: core.Bot = bot
        self.ctxmenu: app_commands.ContextMenu = app_commands.ContextMenu(
            name="Message to MystBin",
            callback=self.convert_mystbin,
            allowed_installs=ALLOWED_INSTALL,
            allowed_contexts=ALLOWED_CONTEXT,
        )

        self.session: aiohttp.ClientSession | None = None
        self.cache: core.LRUCache[int, Node] = core.LRUCache(50)

    async def cog_load(self) -> None:
        self.ctxmenu.on_error = self.mystbin_error
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

    async def _fetch_paste(self, identifier: str) -> PasteFetch:
        assert self.session

        async with self.session.get(f"{MYSTBIN_API}/{identifier}") as resp:
            resp.raise_for_status()

            data: PasteFetch = await resp.json()
            return data

    @app_commands.checks.cooldown(2, 10.0)
    async def convert_mystbin(self, interaction: discord.Interaction[core.Bot], message: discord.Message) -> None:
        assert self.session
        await interaction.response.defer()

        # First check our cache...
        # This doesn't technically save a request, but it *does* save a POST request in most cases...
        cached: Node | None = self.cache.get(message.id, None)
        if cached and cached.last_edit == message.edited_at:
            try:
                paste: PasteFetch = await self._fetch_paste(cached.identifier)
            except aiohttp.ClientResponseError as e:
                if e.status != 404:
                    await interaction.followup.send(f"An unknown error occurred fetching this paste: `{e.status}`")
                    return
            else:
                await interaction.followup.send(f"{MYSTBIN_URL}{paste['id']}")
                return

        parsed: core.CodeBlocks = core.CodeBlocks.convert(message.content)
        files: list[MBFileCreate] = []
        content: str

        for attachment in message.attachments:
            content_type: str = attachment.content_type or ""
            if content_type.startswith("text/") or content_type == "application/json":
                content = (await attachment.read()).decode("UTF-8")
                filename: str = attachment.filename.removesuffix(".txt")

                files.append({"filename": filename, "content": content[:300_000]})

        for index, block in enumerate(parsed.blocks, 1):
            name = f"block_{index}.{block['language'] or 'txt'}"
            files.append({"filename": name, "content": block["content"]})

        if len(files) < 5:
            content = (
                f"{message.author}({message.author.id}) in {message.channel}({message.channel.id})\n"
                f"{message.created_at}\n\n{message.content}"
            )
            files.append({"filename": f"{message.id}.txt", "content": content})

        async with self.session.post(MYSTBIN_API, json={"files": files[:5]}) as resp:
            if resp.status != 200:
                await interaction.followup.send(f"An error occurred creating this paste: `{resp.status}`")
                return

            data: PasteCreateResp = await resp.json()
            identifier: str = data["id"]
            url: str = f"{MYSTBIN_URL}{identifier}"

            node: Node = Node(identifier=identifier, last_edit=message.edited_at)
            self.cache[message.id] = node

            await interaction.followup.send(url)

    async def mystbin_error(
        self, interaction: discord.Interaction[core.Bot], error: app_commands.AppCommandError
    ) -> None:
        send = interaction.response.send_message
        if interaction.response.is_done():
            send = interaction.followup.send

        await send(f"An error occurred: {error}", ephemeral=True)


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(MystBin(bot))

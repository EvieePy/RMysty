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
import re
from typing import Any

import aiohttp
import discord
from discord.app_commands import ContextMenu
from discord.ext import commands

import core


URL_REGEX: re.Pattern[str] = re.compile(
    r"(?P<URL>[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*))",
    re.IGNORECASE,
)
CHII_BASE: str = core.config["CHII"]["url"]


class Chii(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None

        self.chii_menu: ContextMenu = ContextMenu(name="Shorten URL", callback=self.shorten_url)

    async def cog_load(self) -> None:
        self.bot.tree.add_command(self.chii_menu)
        self.session = aiohttp.ClientSession()

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.chii_menu.name, type=self.chii_menu.type)

    async def shorten_url(self, interaction: discord.Interaction, message: discord.Message) -> None:
        assert self.session is not None

        await interaction.response.defer()

        content: str = discord.utils.remove_markdown(message.content)
        match: re.Match[str] | None = URL_REGEX.search(content)

        if not match or not match.group("URL"):
            await interaction.followup.send("There is no valid URL in this message.")
            return

        url: str = match.group("URL").removeprefix("<").removesuffix(">")
        if len(url) < 25:
            await interaction.followup.send("URL must be 25 charcters or longer.")
            return

        elif not url.startswith(("http://", "https://")):
            await interaction.followup.send('URL must contain either "http://" or "https://"')
            return

        async with self.session.post(f"{CHII_BASE}/create", json={"url": url}) as resp:
            if resp.status == 400:
                error: dict[str, Any] = await resp.json()
                await interaction.followup.send(f"Unable to shorten URL: {error['error']}")
                return

            elif resp.status > 200:
                await interaction.followup.send(f"An unknown error occurred. Please try again later: `{resp.status}`")
                return

            data: dict[str, Any] = await resp.json()
            await interaction.followup.send(f"<{data['url']}>")


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Chii(bot))

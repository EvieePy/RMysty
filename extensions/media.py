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

import discord
import wavelink
from discord.app_commands import ContextMenu
from discord.ext import commands

import core


SPOTIFY_URL_REGEX: re.Pattern[str] = re.compile(
    r"(http(s)?://open.)?"
    r"(spotify)"
    r"(.com/|:)(?P<type>album|playlist|artist|track)"
    r"([/:])(?P<id>[a-zA-Z0-9]+)"
    r"([?&]si=[a-zA-Z0-9]+)?([?&]dl_branch=[0-9]+)?"
)


class MediaConverter(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot = bot
        self.ctxmenu: ContextMenu = ContextMenu(name="Spotify to Youtube", callback=self.convert_spotify)

    async def cog_load(self) -> None:
        self.bot.tree.add_command(self.ctxmenu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctxmenu.name, type=self.ctxmenu.type)

    async def convert_spotify(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.defer()

        content: str = discord.utils.remove_markdown(message.content)
        match: re.Match[str] | None = SPOTIFY_URL_REGEX.search(content)

        if not match or not match.group("type"):
            await interaction.followup.send("There is no valid Spotify URL in this message.")
            return

        if match.group("type") != "track":
            await interaction.followup.send("Only Spotify tracks are supported.")
            return

        tracks: wavelink.Search = await wavelink.Playable.search(match.group(0), source="spotify")
        if not tracks:
            await interaction.followup.send("Unable to find a Spotify track matching this URL.")
            return

        track: wavelink.Playable = tracks[0]
        if not track.isrc:
            await interaction.followup.send("This Spotify track does not have an ISRC and can not be looked up.")
            return

        youtube: wavelink.Search = await wavelink.Playable.search(f'"{track.isrc}"', source="ytsearch:")
        if not youtube:
            await interaction.followup.send("This Spotify track does not have an ISRC associated with it on YouTube.")
            return

        assert youtube[0].uri is not None
        await interaction.followup.send(youtube[0].uri)


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(MediaConverter(bot))

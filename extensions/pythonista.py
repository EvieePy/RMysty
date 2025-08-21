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

from __future__ import annotations

import asyncio
import datetime
import logging
import re
from collections import defaultdict
from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

import core


logger: logging.Logger = logging.getLogger(__name__)


PYTHONISTA: int = 490948346773635102
TIME: int = 859565527343955998
BUNNIE: int = 719993112596054028

BYPASS_ROLES: tuple[int, ...] = (
    570452583932493825,
    1064477988013477939,
    986107886470049892,
    1099565946403836015,
    1160372911853555814,
    873944105598738462,
    862802293891530812,
)

GENERAL_CHANNELS: tuple[int, ...] = (490950520412831746, 1292898281931935938, 916551676448636969)
TIO_TESTER: int = 1286823927540219916
HONEY_ROLE: int = 1292886539877093549
BEE_CHANNELS: tuple[int, ...] = (1292898281931935938, 490950520412831746, 1006716547223519293, 490951172673372195)

CHANNEL_SPREAD: int = 3
CHANNEL_SPREAD_RATE: float = 5

URL_REGEX: re.Pattern[str] = re.compile(
    r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", re.IGNORECASE
)
AI_REGEX: re.Pattern[str] = re.compile(r"\S+\.ai")

URL_MAX: int = 3


class Pythonista(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot: core.Bot = bot

        self._channel_spread: dict[int, set[int]] = defaultdict(set)
        self._tasks: set[asyncio.Task[None]] = set()

    def _check_current_member(self, member: discord.Member) -> bool:
        guild: discord.Guild | None = self.bot.get_guild(PYTHONISTA)
        if not guild:
            return False

        return member in guild.members

    async def _do_ban(self, member: discord.Member, *, reason: str = "No reason given...") -> None:
        try:
            await member.ban(delete_message_days=1, reason=f"AutoBan: {reason}")
            if member.guild.id == BUNNIE:
                channel: discord.TextChannel = member.guild.get_channel(725130035069059198)  # type: ignore
                if not channel:
                    return

                await channel.send(f"{member.mention}`(ID: {member.id})[{member.global_name}] was banned for: `{reason}`.")
        except discord.HTTPException as e:
            if not self._check_current_member(member):
                return

            webhook: discord.Webhook = discord.Webhook.from_url(core.config["PYTHONISTA"]["logs"], client=self.bot)
            await webhook.send(
                f"Unable to ban user for `{reason}`: `{member} (ID: {member.id})` > `{e}`",
                username="RMysty AutoMod",
            )

    async def _spread_waiter(self, member: discord.Member, *, rate: float = CHANNEL_SPREAD_RATE) -> None:
        await asyncio.sleep(rate)

        spread = self._channel_spread[member.id]
        if len(spread) >= CHANNEL_SPREAD:
            await self._do_ban(member, reason="Spamming across channels")

        spread.clear()

    async def cog_unload(self) -> None:
        for task in self._tasks:
            try:
                task.cancel()
            except Exception as e:
                logger.debug("Failed to cancel running spread task: %s", e)

    def is_new(self, member: discord.Member, hours: int = 24) -> bool:
        joined: datetime.datetime | None = member.joined_at
        if not joined:
            return False

        now: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)
        delta: datetime.timedelta = datetime.timedelta(hours=hours)

        return joined + delta >= now

    def url_count(self, content: str) -> int:
        matches = URL_REGEX.findall(content)
        return len(matches)

    @commands.Cog.listener("on_message")
    async def on_message_bunnie(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if not message.guild or message.guild.id != BUNNIE:
            return

        author: discord.Member = cast(discord.Member, message.author)
        if author.guild_permissions.kick_members:
            return

        if "nigger" in message.content or "nigga" in message.content:
            await self._do_ban(author, reason="Racist Slurs")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if not message.guild or message.guild.id not in (PYTHONISTA, TIME, BUNNIE):
            return

        author: discord.Member = cast(discord.Member, message.author)
        if any(r.id in BYPASS_ROLES for r in author.roles):
            return

        if author.guild_permissions.kick_members:
            return

        # Increase the time we wait for spread on new joins...
        rate: float = 15.5 if self.is_new(author) else CHANNEL_SPREAD_RATE

        spread = self._channel_spread[author.id]
        if not spread:
            task: asyncio.Task[None] = asyncio.create_task(self._spread_waiter(author, rate=rate))
            task.add_done_callback(lambda t: self._tasks.remove(t))
            self._tasks.add(task)

        spread.add(message.channel.id)

    @commands.Cog.listener("on_message")
    async def on_message_ot(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if message.channel.id not in GENERAL_CHANNELS:
            return

        assert isinstance(message.author, discord.Member)
        member: discord.Member = message.author

        if any(r.id in BYPASS_ROLES for r in member.roles):
            return

        if member.guild_permissions.kick_members:
            return

        if not self.is_new(member):
            return

        if member.get_role(HONEY_ROLE) and message.channel.id in BEE_CHANNELS:
            return await self._do_ban(member, reason="Honeypot")

        content: str = message.content

        if AI_REGEX.findall(content):
            return await self._do_ban(member, reason="Suspected Advertising/Spam (New Member)")

        urls: int = self.url_count(content)
        if urls > URL_MAX and self.is_new(member, hours=1):
            return await self._do_ban(member, reason="URL Spam (New Member)")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if after.bot:
            return

        if after.guild.id != PYTHONISTA:
            return

        if any(r.id in BYPASS_ROLES for r in after.roles):
            return

        if after.guild_permissions.kick_members:
            return

        if after.flags.did_rejoin:
            return

        if before.flags.completed_onboarding:
            return

        if not after.flags.completed_onboarding:
            return

        if not after.get_role(HONEY_ROLE):
            return

        await self._do_ban(after, reason="Honeypot")

    @app_commands.command()
    @app_commands.guilds(discord.Object(PYTHONISTA))
    @app_commands.checks.cooldown(2, 60.0)
    async def tester(self, interaction: discord.Interaction[core.Bot]) -> None:
        """Add or remove yourself from the TwitchIO Tester role."""
        assert interaction.guild

        member: discord.Member = cast(discord.Member, interaction.user)

        role: discord.Role | None = member.get_role(TIO_TESTER)
        if role:
            try:
                await member.remove_roles(role)
            except Exception:
                await interaction.response.send_message("An unknown error occurred. Try again later...", ephemeral=True)
            else:
                await interaction.response.send_message("Successfully removed from `Twitchio Tester`", ephemeral=True)

            return

        role = interaction.guild.get_role(TIO_TESTER)
        assert role

        try:
            await member.add_roles(role)
        except Exception:
            await interaction.response.send_message("An unknown error occurred. Try again later...", ephemeral=True)
        else:
            await interaction.response.send_message("Successfully added to `Twitchio Tester`", ephemeral=True)


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Pythonista(bot))

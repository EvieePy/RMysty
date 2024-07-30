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
import logging
from collections import defaultdict
from typing import cast

import discord
from discord.ext import commands

import core


logger: logging.Logger = logging.getLogger(__name__)


PYTHONISTA: int = 490948346773635102
BYPASS_ROLES: tuple[int, ...] = (
    570452583932493825,
    1064477988013477939,
    986107886470049892,
)

CHANNEL_SPREAD: int = 3
CHANNEL_SPREAD_RATE: float = 3.5


class Pythonista(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot: core.Bot = bot

        self._channel_spread: dict[int, set[int]] = defaultdict(set)
        self._tasks: set[asyncio.Task[None]] = set()

    async def _spread_waiter(self, member: discord.Member) -> None:
        await asyncio.sleep(CHANNEL_SPREAD_RATE)

        spread = self._channel_spread[member.id]
        if len(spread) >= CHANNEL_SPREAD:
            try:
                await member.ban(delete_message_days=1, reason="AutoBan: Spamming messages across channels.")
            except discord.HTTPException as e:
                webhook: discord.Webhook = discord.Webhook.from_url(core.config["PYTHONISTA"]["logs"], client=self.bot)
                await webhook.send(
                    f"Unable to ban user for Channel Spread Spam: `{member} (ID: {member.id})` > `{e}`",
                    username="RMysty AutoMod",
                )

        spread.clear()

    async def cog_unload(self) -> None:
        for task in self._tasks:
            try:
                task.cancel()
            except Exception as e:
                logger.debug("Failed to cancel running spread task: %s", e)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if not message.guild or message.guild.id != PYTHONISTA:
            return

        author: discord.Member = cast(discord.Member, message.author)
        if any(r.id in BYPASS_ROLES for r in author.roles):
            return

        if author.guild_permissions.kick_members:
            return

        spread = self._channel_spread[author.id]
        if not spread:
            task: asyncio.Task[None] = asyncio.create_task(self._spread_waiter(author))
            task.add_done_callback(lambda t: self._tasks.remove(t))
            self._tasks.add(task)

        spread.add(message.channel.id)


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Pythonista(bot))

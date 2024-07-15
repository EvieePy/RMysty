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

from typing import TYPE_CHECKING, Any, Literal

import discord
from discord import app_commands
from discord.ext import commands


if TYPE_CHECKING:
    import core


type CommandT = app_commands.Command[Admin, ..., Any] | app_commands.ContextMenu


class Admin(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot: core.Bot = bot
        self.logs: discord.TextChannel | None = None

    async def cog_load(self) -> None:
        self.logs = await self.bot.fetch_channel(1262457734746472508)  # type: ignore

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self,
        ctx: commands.Context[core.Bot],
        guilds: commands.Greedy[discord.Object],
        spec: Literal["~", "*", "^"] | None = None,
    ) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)  # type: ignore
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction[core.Bot], command: CommandT) -> None:
        if not self.logs:
            return

        user: discord.Member | discord.User = interaction.user
        channel: str = str(interaction.channel) if interaction.channel else "DM"
        message = f"`{user} ({user.id})` used `{command.qualified_name}` in **`{interaction.guild} - (#{channel})`**"

        await self.logs.send(message)


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Admin(bot))

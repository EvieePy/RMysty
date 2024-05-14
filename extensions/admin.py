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

from typing import Literal

import discord
from discord.ext import commands

import core


class Admin(commands.Cog):
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
    
    @commands.hybrid_command()
    async def cleangif(self, ctx: commands.Context[core.Bot], *, member_: str) -> None:
        if not ctx.guild:
            return
        
        if not ctx.channel.permissions_for(ctx.author).manage_messages:  # type: ignore
            return
        
        await ctx.defer()
        
        try:
            member: discord.Member = await commands.MemberConverter().convert(ctx, member_)
        except commands.MemberNotFound:
            await ctx.send("Could not find that member!")
            return
        
        count: int = 0
        async for message in ctx.channel.history(limit=20):
            if count >= 5:
                break
            
            if message.author == member and message.embeds:
                for embed in message.embeds:
                    if embed.type in ("gifv", "image"):
                        try:
                            await message.delete()
                        except discord.HTTPException:
                            pass
                        else:
                            count += 1
                            
                        break
        
        if count:
            await ctx.send(f"Deleted {count} messages with GIFs from: {member.mention}", silent=True)
        else:
            await ctx.send("No messages were deleted.")
            
            
async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Admin(bot))

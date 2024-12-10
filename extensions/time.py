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

import discord
import pytz
from discord import app_commands
from discord.ext import commands

import core


class Time(commands.Cog):
    ALLOWED_INSTALL: app_commands.AppInstallationType = app_commands.AppInstallationType(user=True, guild=True)
    ALLOWED_CONTEXT: app_commands.AppCommandContext = app_commands.AppCommandContext(
        guild=True,
        dm_channel=True,
        private_channel=True,
    )

    time_group = app_commands.Group(
        name="time",
        description="Time/Timezone related commands.",
        allowed_installs=ALLOWED_INSTALL,
        allowed_contexts=ALLOWED_CONTEXT,
    )

    def __init__(self, bot: core.Bot) -> None:
        self.bot = bot

    def build_embed(self, user: discord.User, dt: datetime.datetime) -> discord.Embed:
        colour = 1513835 if dt.hour <= 6 or dt.hour >= 18 else 15460239

        embed = discord.Embed(title="Timezone Infomation", description=f"{dt}", colour=colour)
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)

        offset = datetime.datetime.utcoffset(dt) or datetime.timedelta(hours=0)
        long = dt.strftime("%A, %d %B %Y, %H:%M:%S")
        short = dt.strftime("%H:%M %p")

        embed.description = (
            f"### `{dt.tzname()} | {'+' if offset.seconds > -1 else '-'}{offset} UTC`\n`{long}`\n`({short})`"
        )

        return embed

    @time_group.command(name="set")
    async def time_set(self, interaction: discord.Interaction, *, timezone: str) -> None:
        """Set your current timezone information.

        Parameters
        ----------
        timezone: str
            Your current timezone. E.g. "US/Eastern" or "Europe/London".
        """
        await interaction.response.defer(ephemeral=True)

        if timezone not in pytz.all_timezones:
            await interaction.followup.send(f"`{timezone}` is not a valid timezone.")
            return

        await self.bot.database.set_user_timezone(uid=interaction.user.id, timezone=timezone)
        await interaction.followup.send(f"Set your current timezone to `{timezone}` successfully.")

    @time_group.command(name="fetch")
    async def time_get(self, interaction: discord.Interaction, *, user: discord.User | None = None) -> None:
        """Get the current timezone and time for a user.

        user: discord.User | None
            The user to retrieve time info for. Defaults to yourself.
        """
        await interaction.response.defer()
        resolved: discord.User | None = None

        if isinstance(user, (discord.User, discord.Member)):
            resolved = user

        elif user is None:
            resolved = interaction.user  # type: ignore

        if not resolved:
            await interaction.followup.send(f"The user: `{user}` could not be found.")
            return

        result = await self.bot.database.fetch_user_timezone(uid=resolved.id)
        if not result:
            await interaction.followup.send(f"`{resolved}` has no timezone set.")
            return

        tz = pytz.timezone(result.timezone)
        utc = datetime.datetime.now(tz=datetime.UTC)
        local_ = utc.astimezone(tz=tz)

        embed = self.build_embed(resolved, local_)
        await interaction.followup.send(embed=embed)

    @time_set.autocomplete(name="timezone")
    async def time_set_autocomplete(
        self, interation: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        matches = core.extract_or_exact(current, pytz.all_timezones, limit=20, score_cutoff=50)
        results = [app_commands.Choice(name=m[0], value=m[0]) for m in matches]

        return results


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Time(bot))
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

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.app_commands import ContextMenu
from discord.ext import commands

import core


if TYPE_CHECKING:
    from database.models import ModeratorNote
    from types_.notes import ModeratorNoteData


PYTHONISTA_GUILD: int = 490948346773635102
DPY_GUILD: int = 336642139381301249
TIMEGUILD: int = 859565527343955998
DWAREGUILD: int = 149998214810959872

WHITELISTED_ROLES: list[int] = [
    558559632637952010,
    490952483238313995,
    1130880992652046449,
    578255729295884308,
    862802293891530812,
    872385548646490122,
]
WHITELISTED_GUILDS: list[int] = [PYTHONISTA_GUILD, DPY_GUILD, TIMEGUILD, DWAREGUILD]


class ModNotes(commands.Cog):
    def __init__(self, bot: core.Bot) -> None:
        self.bot: core.Bot = bot

        USER_INSTALL: app_commands.AppInstallationType = app_commands.AppInstallationType(user=True)
        self._add_note: ContextMenu = ContextMenu(
            name="Add Moderator Note",
            callback=self.add_note,
            allowed_installs=USER_INSTALL,
        )
        self._get_notes: ContextMenu = ContextMenu(
            name="View Moderator Notes",
            callback=self.get_notes,
            allowed_installs=USER_INSTALL,
        )

    async def cog_load(self) -> None:
        self.bot.tree.add_command(self._add_note)
        self.bot.tree.add_command(self._get_notes)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self._add_note.name, type=self._add_note.type)
        self.bot.tree.remove_command(self._get_notes.name, type=self._get_notes.type)

    def permissions_check(self, interaction: discord.Interaction[core.Bot]) -> bool:
        user: discord.Member | discord.User = interaction.user

        if not isinstance(user, discord.Member):
            return False

        if interaction.guild is None:
            return False

        if interaction.guild.id not in WHITELISTED_GUILDS:
            return False

        if not user.resolved_permissions:
            return False

        if user.resolved_permissions.moderate_members:
            return True

        return False

    async def whitelist_check(self, interaction: discord.Interaction[core.Bot]) -> bool:
        user: discord.Member | discord.User = interaction.user

        if not isinstance(user, discord.Member):
            return False

        for guild_id in WHITELISTED_GUILDS:
            guild: discord.Guild | None = self.bot.get_guild(guild_id)
            if guild is None:
                continue

            member: discord.Member | None = guild.get_member(user.id)
            if member is None:
                continue

            if [r for r in member.roles if r.id in WHITELISTED_ROLES]:
                return True

        # TODO: Add database check for whitelisted users. (Hence async)
        return False

    async def add_note(self, interaction: discord.Interaction[core.Bot], member: discord.Member) -> None:
        if not self.permissions_check(interaction) and not await self.whitelist_check(interaction):
            await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
            return

        if not interaction.guild:
            return

        if interaction.user.id == member.id:
            await interaction.response.send_message("You cannot add a note to yourself.", ephemeral=True)
            return

        if member.id == interaction.client.user.id:  # type: ignore
            await interaction.response.send_message("You cannot add a note to me :(", ephemeral=True)
            return

        modal: core.NotesModal = core.NotesModal()
        await interaction.response.send_modal(modal)

        await modal.wait()
        if not modal.note:
            return

        data: ModeratorNoteData = {
            "user_id": member.id,
            "moderator_id": interaction.user.id,
            "guild_id": interaction.guild.id,
            "event": 0,
            "additional": None,
            "note": modal.note.value,
            "channel_id": None,
            "message_id": None,
        }

        note_id: int = await self.bot.database.add_moderator_notes(data)
        await interaction.followup.send(f"Moderator note **`({note_id})`** added successfully.", ephemeral=True)

    async def get_notes(self, interaction: discord.Interaction[core.Bot], member: discord.Member) -> None:
        """View moderation notes for a user."""
        await interaction.response.defer(ephemeral=True)

        if not self.permissions_check(interaction) and not await self.whitelist_check(interaction):
            await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
            return

        notes: list[ModeratorNote] = await self.bot.database.fetch_moderator_notes(member.id)
        if not notes:
            await interaction.followup.send("No moderation notes found for this user.", ephemeral=True)
            return

        view: core.NotesView = core.NotesView(bot=self.bot, notes=notes)
        await view.setup()

        await interaction.followup.send(embed=view.pages[0], view=view, ephemeral=True)


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(ModNotes(bot))

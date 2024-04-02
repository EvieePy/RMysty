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

import discord
from discord import ui

import core
from database.models import ModeratorNote


__all__ = ("NotesView", "NotesModal")


COLOURS: dict[int, int] = {
    0: 6567895,
}


class PageModal(ui.Modal, title="Select Page"):
    page: ui.TextInput[ui.View] = ui.TextInput(
        label="Page Number",
        placeholder="Enter the page number...",
        min_length=1,
        max_length=3,
        required=True,
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.stop()
        await interaction.response.defer()


class NotesView(ui.View):
    def __init__(self, bot: core.Bot, *, notes: list[ModeratorNote]) -> None:
        super().__init__(timeout=300)
        self.bot: core.Bot = bot

        self.notes: list[ModeratorNote] = notes
        self.pages: list[discord.Embed] = []

        self.position: int = 0
        self.total: int = len(notes)

        self.has_setup: bool = False

    async def setup(self) -> None:
        user: discord.User = await self.bot.fetch_user(self.notes[0].user_id)
        seen: dict[int, discord.Member | discord.User] = {}

        for index, note in enumerate(self.notes, 1):
            guild: discord.Guild | None = self.bot.get_guild(note.guild_id)
            mod: discord.Member | discord.User | None = seen.get(note.moderator_id, None)

            if guild is not None and not mod:
                mod = guild.get_member(note.moderator_id)

            if not mod:
                mod = await self.bot.fetch_user(note.moderator_id)

            seen[note.moderator_id] = mod

            embed: discord.Embed = discord.Embed(colour=COLOURS[note.event.value], timestamp=note.timestamp)
            embed.set_author(
                name=f"{user.display_name}",
                icon_url=user.display_avatar.url,
                url=f"https://discord.com/users/{user.id}",
            )

            embed.description = note.note
            embed.add_field(name="Additional", value=note.additional or "None", inline=False)

            embed.add_field(name="User", value=f"{user.mention} `({user.id})`", inline=False)
            embed.add_field(name="Moderator", value=f"{mod.mention} `({mod.id})`", inline=False)

            embed.add_field(name="Event", value=f"`{note.event.name}`")
            embed.add_field(name="Guild", value=f"`{getattr(guild, 'name', 'Unknown')}`")
            embed.add_field(name="Note ID", value=f"`{note.id}`")

            embed.set_footer(text=f"Page {index}/{self.total}")

            self.pages.append(embed)

    async def on_timeout(self) -> None:
        self.stop()

    @ui.button(emoji="\u25c0\ufe0f", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction[core.Bot], button: ui.Button[ui.View]) -> None:
        await interaction.response.defer()

        if self.position == 0:
            return

        self.position -= 1
        await interaction.edit_original_response(embed=self.pages[self.position])

    @ui.button(label="Go to...", style=discord.ButtonStyle.grey)
    async def goto(self, interaction: discord.Interaction[core.Bot], button: ui.Button[ui.View]) -> None:
        assert interaction.channel

        modal: PageModal = PageModal()
        await interaction.response.send_modal(modal)

        await modal.wait()
        if not modal.page:
            return

        try:
            number: int = min(max(int(modal.page.value), 1), self.total)
        except ValueError:
            await interaction.followup.send("Invalid page number, please try again.", ephemeral=True)
            return

        self.position = number - 1
        await interaction.edit_original_response(embed=self.pages[self.position])

    @ui.button(emoji="\u25b6\ufe0f", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction[core.Bot], button: ui.Button[ui.View]) -> None:
        await interaction.response.defer()

        if self.position == self.total - 1:
            return

        self.position += 1
        await interaction.edit_original_response(embed=self.pages[self.position])

    @ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction[core.Bot], button: ui.Button[ui.View]) -> None:
        await interaction.response.defer()

        await interaction.delete_original_response()
        self.stop()


class NotesModal(ui.Modal, title="Add Moderator Note"):
    note: ui.TextInput[ui.View] = ui.TextInput(
        label="Moderation Note",
        placeholder="Enter your note...",
        min_length=10,
        max_length=4000,
        required=True,
        style=discord.TextStyle.paragraph,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.stop()
        await interaction.response.defer()

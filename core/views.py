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
import io
import math
from typing import TYPE_CHECKING, Self

import discord
import numpy as np
from discord import ui
from PIL import Image, ImageDraw, ImageFont

import core


if TYPE_CHECKING:
    from types_.colours import COORDS_FT, RGB_T

    from ..database.models import PasteRecord


__all__ = ("ColourView", "ConfirmView", "CountdownView", "MBPasteView", "PageModal")


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


class ColourView(ui.View):
    embed: discord.Embed
    image_file: discord.File
    thumb_file: discord.File

    def __init__(self, *, timeout: float | None = 300, colour: core.Colour, bot: core.Bot) -> None:
        self.colour: core.Colour = colour
        self.bot: core.Bot = bot

        super().__init__(timeout=timeout)

        self._MULTIPLIER: int = 5
        self._BW: int = 500
        self._BH: int = 650
        self._W: int = self._BW * self._MULTIPLIER
        self._H: int = self._BH * self._MULTIPLIER
        self._BGAP: int = 25
        self._GAP: int = self._BGAP * self._MULTIPLIER

        self._BOX_H: int = 85 * self._MULTIPLIER
        self._CIR_H: int = 135 * self._MULTIPLIER
        self._FACTOR: float = 0.125
        self._OW: int = 5 * self._MULTIPLIER

        self._GREY: core.Colour = core.Colour.from_hex("#bababa")

    def _clamp(self, v: float, /) -> int:
        return max(0, min(int(v), 255))

    def _generate_gradient(self) -> Image.Image:
        h = self._H - (self._GAP * 2)
        w = self._GAP * 2

        r, g, b = self.colour.rgb
        gr, gg, gb = self._GREY.rgb

        gradient = np.zeros((w, h, 3), np.uint8)
        gradient[:, :, 0] = np.linspace(r, gr, h, dtype=np.uint8)
        gradient[:, :, 1] = np.linspace(g, gg, h, dtype=np.uint8)
        gradient[:, :, 2] = np.linspace(b, gb, h, dtype=np.uint8)

        return Image.fromarray(gradient).rotate(90, expand=True)

    def _get_shade_tint(self, *, shade: bool = False, factor: float) -> RGB_T:
        rgb: list[int] = []

        for v in self.colour.rgb:
            if shade:
                rgb.append(self._clamp(v * (1 - factor)))
            else:
                rgb.append(self._clamp(v + (255 - v) * factor))

        return tuple(rgb)  # type: ignore

    def _get_luminence(self, rgb: RGB_T) -> str:
        # https://stackoverflow.com/a/58270890
        r, g, b = rgb
        hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))

        if hsp > 127.5:
            return "black"
        else:
            return "white"

    def _generate_contrast_indicator(self, image: Image.Image, colour: core.Colour) -> Image.Image:
        draw = ImageDraw.Draw(image)

        x = self._GAP
        y = self._CIR_H
        coords: COORDS_FT = (x, x, y, y)

        draw.ellipse(coords, outline=colour.rgb, width=self._OW, fill=colour.rgb)
        return image

    def _generate_box_points(self, image: Image.Image, *, original: COORDS_FT) -> Image.Image:
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(image, mode="RGBA")

        x1 = original[2] - self._OW  # Right most...
        x2 = original[2] - (self._BOX_H / 2)  # inner point...

        y1 = original[1] + self._OW  # Top most...
        y2 = y1 + (self._BOX_H / 2)  # Center Point...
        # y3 = original[3] - self._OW  # Bottom most...

        draw.polygon(((x1, y1), (x2, y1), (x1, y2)), fill="black")
        draw.polygon(((x1, y2), (x2, y1), (x2, y2)), fill="white")

        return image

    def _generate_box(self, image: Image.Image, *, rgb: RGB_T, coords: COORDS_FT, factor: float) -> Image.Image:
        outline: str = self._get_luminence(rgb)
        colour: core.Colour = core.Colour.from_hex("#%02x%02x%02x" % rgb)

        draw: ImageDraw.ImageDraw = ImageDraw.Draw(image, mode="RGBA")
        draw.rectangle(coords, outline=rgb, fill=rgb, width=2 * self._MULTIPLIER)

        font = ImageFont.truetype("assets/fonts/Nunito-SemiBold.ttf", 20 * self._MULTIPLIER)
        gap: float = self._BGAP * 4

        text: str = f"{colour:html}  {'<' if colour == self.colour else ''}"
        bottom: str = self.bot.colours.get(colour.html.lower(), "")

        draw.text((coords[0] + gap, coords[1] + gap), text, fill=outline, outline=outline, font=font)  # type: ignore
        draw.text(  # type: ignore
            ((coords[0] + gap, (coords[1] + self._BOX_H) - (gap * 2))), bottom, fill=outline, outline=outline, font=font
        )

        return self._generate_box_points(image, original=coords)

    def _generate_rgb_box(self, image: Image.Image) -> Image.Image:
        rgb = self.colour.rgb
        r, g, b = (rgb[0], 0, 0), (0, rgb[1], 0), (0, 0, rgb[2])
        base = [((255, 0, 0), "R"), ((0, 255, 0), "G"), ((0, 0, 255), "B")]

        draw: ImageDraw.ImageDraw = ImageDraw.Draw(image, mode="RGBA")

        for i, v in enumerate((r, g, b), 0):
            x1 = (self._GAP * 4) + ((self._GAP * 3) * i)
            y1 = self._H - (self._GAP * 3)
            x2 = x1 + (self._GAP * 2)
            y2 = self._H - self._GAP

            draw.rectangle((x1, y1, x2, y2), fill=v, outline=base[i][0], width=self._OW)

            font = ImageFont.truetype("assets/fonts/Nunito-SemiBold.ttf", 18 * self._MULTIPLIER)
            draw.text(  # type: ignore
                (x1 + self._GAP // 2 - self._OW, y1 + self._OW), base[i][1], fill="white", outline="white", font=font
            )
            draw.text(  # type: ignore
                (x1 + self._GAP // 2 - self._OW, y1 + self._GAP), str(rgb[i]), fill="white", outline="white", font=font
            )

        return image

    def _generate_image(self) -> io.BytesIO:
        image: Image.Image
        image = Image.new("RGBA", (self._W, self._H), (0, 0, 0, 0))

        for i, n in enumerate(range(-2, 3, 1)):
            factor: float = self._FACTOR * abs(n)

            if n == 0:
                rgb: RGB_T = self.colour.rgb
            elif n > 0:
                rgb = self._get_shade_tint(shade=True, factor=factor)
            else:
                rgb = self._get_shade_tint(factor=factor)

            x1 = (self._GAP * 2) * 2
            y1 = self._GAP + (self._GAP * i) + (self._BOX_H * i)
            y2 = y1 + self._BOX_H
            x2 = self._W - self._GAP

            coords: COORDS_FT = (x1, y1, x2, y2)
            image = self._generate_box(image, rgb=rgb, coords=coords, factor=factor)

        # image = self._generate_contrast_indicator(image, colour=self.colour)

        # Generate the gradient bar...
        gradient: Image.Image = self._generate_gradient()
        image.paste(gradient, (self._GAP, self._GAP))

        # Generate the RGB Boxes...
        image = self._generate_rgb_box(image=image)

        # Anti-Aliasing and saving...
        image = image.resize((self._BW, self._BH), Image.LANCZOS)

        buffer: io.BytesIO = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    def _generate_thumb(self) -> io.BytesIO:
        image: Image.Image
        image = Image.new("RGB", (200, 200), self.colour.rgb)

        buffer: io.BytesIO = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    async def prepare(self) -> None:
        self.embed = discord.Embed(title=f"Colour Information | {self.colour:html}", colour=self.colour.code)

        name: str = self.bot.colours.get(self.colour.html.lower(), "No colour name found...")
        self.embed.description = f"```\n{name}\n```"

        self.embed.add_field(name="HTML", value=f"`{self.colour.html}`")
        self.embed.add_field(name="HEX", value=f"`{self.colour.hex}`")
        self.embed.add_field(name="HEX Clean", value=f"`{self.colour.hex_clean}`")

        self.embed.add_field(name="Base 10", value=f"`{self.colour.code}`")
        self.embed.add_field(name="RGB", value=f"`{self.colour.rgb}`")
        self.embed.add_field(name="HLS", value=f"`{self.colour.hls}`")

        self.embed.add_field(name="RGB Coords", value="\n".join([f"`{v}`" for v in self.colour.rgb_coords]))
        self.embed.add_field(name="HLS Coords", value="\n".join([f"`{v}`" for v in self.colour.hls_coords]))

        buffer = await asyncio.to_thread(self._generate_image)
        thumb_buffer = await asyncio.to_thread(self._generate_thumb)

        self.image_file: discord.File = discord.File(fp=buffer, filename=f"{self.colour.hex_clean}.png")
        self.thumb_file: discord.File = discord.File(fp=thumb_buffer, filename=f"{self.colour.hex_clean}_thumb.png")

        self.embed.set_image(url=f"attachment://{self.colour.hex_clean}.png")
        self.embed.set_thumbnail(url=f"attachment://{self.colour.hex_clean}_thumb.png")


class ConfirmView(ui.View):
    def __init__(self, *, timeout: float | None = 90) -> None:
        self.result: bool = False
        super().__init__(timeout=timeout)

    @ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def confirm(self, interaction: discord.Interaction[core.Bot], button: discord.ui.Button[Self]) -> None:
        self.result = True

        await interaction.response.defer()

        try:
            await interaction.delete_original_response()
        except:
            pass

        self.stop()

    @ui.button(label="Cancel", style=discord.ButtonStyle.blurple)
    async def cancel(self, interaction: discord.Interaction[core.Bot], button: discord.ui.Button[Self]) -> None:
        await interaction.response.defer()

        try:
            await interaction.delete_original_response()
        except:
            pass

        self.stop()


class CountdownView(ui.View):
    def __init__(self, *, timeout: float | None = 90, user_id: int) -> None:
        self.result: bool = False
        self.user_id: int = user_id
        super().__init__(timeout=timeout)

    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        return interaction.user.id == self.user_id

    @ui.button(label="Start", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction[core.Bot], button: discord.ui.Button[Self]) -> None:
        self.result = True

        await interaction.response.defer()

        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

        await interaction.edit_original_response(view=self)
        self.stop()

    @ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction[core.Bot], button: discord.ui.Button[Self]) -> None:
        await interaction.response.defer()

        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

        await interaction.edit_original_response(view=self)
        self.stop()


class MBPasteView(ui.View):
    def __init__(self, bot: core.Bot, *, paste_id: str = "") -> None:
        self.bot: core.Bot = bot
        self.paste_id: str = paste_id

        super().__init__(timeout=None)

        url_button: ui.Button[Self] = ui.Button(label="View Paste", url=f"https://mystb.in/{paste_id}")
        del_button: ui.Button[Self] = ui.Button(label="Delete", style=discord.ButtonStyle.red, custom_id=f"d_{paste_id}")
        del_button.callback = self.del_callback

        self.add_item(url_button)
        self.add_item(del_button)

    async def del_callback(self, interaction: discord.Interaction[core.Bot]) -> None:
        await interaction.response.defer(ephemeral=True)
        user: discord.User | discord.Member = interaction.user

        paste: PasteRecord | None = await self.bot.database.fetch_user_paste(id=self.paste_id, uid=user.id)
        if not paste:
            await interaction.followup.send("Only the message author may delete this paste.", ephemeral=True)
            return

        confirm: ConfirmView = ConfirmView()
        confmsg = (
            "Are you sure you would like to remove this paste? **This action can not be undone.**\n\n"
            "- No one will be able to send this message to MystBin in the future!\n"
            "- If you are worried about tokens: MystBin automatically invalidates all tokens from `Discord`, `Github` and `PyPi`\n"
            "- Someone may have been viewing this paste to assist you; make sure to let them know you removed your paste.\n\n"
        )
        await interaction.followup.send(confmsg, view=confirm, ephemeral=True)
        await confirm.wait()

        if not confirm.result:
            return

        url: str = f"https://mystb.in/api/security/delete/{paste.token}"
        try:
            async with self.bot.session.get(url) as resp:
                resp.raise_for_status()
        except Exception as e:
            await interaction.followup.send(f"An unexpected error occurred, please try again: {e}", ephemeral=True)
            return

        self.bot.blocked_pastes.add(paste.mid)
        await self.bot.database.delete_user_paste(id=self.paste_id, uid=user.id, mid=paste.mid)

        await interaction.followup.send("Successfully removed this paste and data.", ephemeral=True)
        await interaction.delete_original_response()

"""
The MIT License (MIT)

Copyright (c) 2022-Present EvieePy

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import re
from typing import Any

import discord
from discord.ext import commands

import constants
import core


ISSUE_MATCH = re.compile(r'##\d+')

_lib_mapping: dict[int, tuple] = {
    constants.PYTHONISTA.TWITCHIO_CHANNEL: ('twitchio/twitchio', ),
    constants.PYTHONISTA.WAVELINK_CHANNEL: ('pythonistaguild/wavelink', ),
}


GH_API: str = 'https://api.github.com'


class Pythonista(commands.Cog):

    def __init__(self, bot: core.Bot) -> None:
        self.bot = bot

    @property
    def gh_headers(self) -> dict[str, str]:
        auth: str = core.config['TOKENS']['github']

        return {
            'Authorization': f'Bearer {auth}',
            'Accept': 'application/vnd.github+json'
        }

    async def check_issue(self, lib: str, issue: str) -> str | None:
        url: str = f'{GH_API}/repos/{lib}/issues/{issue}'

        async with self.bot.session.get(url, headers=self.gh_headers) as resp:
            if resp.status < 300:
                data: dict[str, Any] = await resp.json()

                return data['html_url']

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if message.guild.id != constants.PYTHONISTA.GUILD_ID:
            return

        match = ISSUE_MATCH.search(message.content)
        if not match:
            return

        _default: tuple = ('twitchio/twitchio', 'pythonistaguild/wavelink', 'rapptz/discord.py')
        libs: tuple = _lib_mapping.get(message.channel.id, _default)

        issue: str = match[0].removeprefix('##')
        valid: list[str] = []

        for lib in libs:
            if url := await self.check_issue(lib, issue):
                valid.append(url)

        if not valid:
            return

        joined: str = '\n'.join(f'<{v}>' for v in valid)
        await message.channel.send(f'Found the following issues for `#{issue}`:\n{joined}')


async def setup(bot: core.Bot) -> None:
    await bot.add_cog(Pythonista(bot))

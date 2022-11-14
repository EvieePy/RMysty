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
import datetime
import pathlib
import tomllib

import aiohttp
import asyncpg
import discord
from discord.ext import commands


with open('./config.toml', 'rb') as fp:
    config = tomllib.load(fp)


class Bot(commands.Bot):

    # noinspection PyDunderSlots, PyUnresolvedReferences
    def __init__(self) -> None:
        intents: discord.Intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(command_prefix=['>? ', '>?'], intents=intents)

        self.started: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)

        self.session: aiohttp.ClientSession | None = None
        self.pool: asyncpg.Pool | None = None

    async def setup_hook(self) -> None:
        modules: list[str] = [f'{p.parent}.{p.stem}' for p in pathlib.Path('modules').glob('*.py')]

        for module in modules:
            await self.load_extension(module)

        self.session = aiohttp.ClientSession()
        self.pool = await asyncpg.create_pool(dsn=config['DATABASE']['dsn'])

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user}(ID: {self.user.id})')

    async def close(self) -> None:
        await super().close()

        await self.session.close()
        await self.pool.close()

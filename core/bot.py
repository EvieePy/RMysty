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
import logging
import pathlib
import tomllib

import aiohttp
import asyncpg
import discord
from discord.ext import commands

from .logs import Handler


with open('./config.toml', 'rb') as fp:
    config = tomllib.load(fp)


logger: logging.Logger = logging.getLogger(__name__)


class Bot(commands.Bot):

    # noinspection PyDunderSlots, PyUnresolvedReferences
    def __init__(self, pool: asyncpg.Pool, session: aiohttp.ClientSession) -> None:
        intents: discord.Intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(command_prefix=['>? ', '>?'], intents=intents)

        self.started: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)

        self.session: aiohttp.ClientSession = session
        self.pool: asyncpg.Pool = pool

        handler: Handler = Handler(level=config['DEBUG']['logging'])
        discord.utils.setup_logging(handler=handler, level=logging.DEBUG)

    async def setup_hook(self) -> None:

        async with self.pool.acquire() as connection:
            with open('./sql/schema.sql', 'r') as schema:
                await connection.execute(schema.read())

        logger.info('Completed initial database setup.')

        modules: list[str] = [f'{p.parent}.{p.stem}' for p in pathlib.Path('modules').glob('*.py')]
        for module in modules:
            await self.load_extension(module)

        logger.info(f'Loaded ({len(modules)}) modules.')

    async def on_ready(self) -> None:
        logger.info(f'Logged in as {self.user}(ID: {self.user.id})')

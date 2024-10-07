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

import asyncio
import logging

import discord

import core
import database


discord.utils.setup_logging(level=core.config["OPTIONS"]["logging"])
LOGGER: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    async def runner() -> None:
        async with database.Database() as db, core.Bot(database=db) as bot:
            await bot.start(core.config["TOKENS"]["discord"])

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to Keyboard Interrupt.")


main()

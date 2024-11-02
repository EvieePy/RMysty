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

import logging
import pathlib

from discord.ext import commands

import core


logger: logging.Logger = logging.getLogger(__name__)


DISABLED = ("extensions.media", "extensions.chii")


async def setup(bot: core.Bot) -> None:
    extensions: list[str] = [f".{f.stem}" for f in pathlib.Path("extensions").glob("*[a-zA-Z].py")]
    loaded: list[str] = []

    for extension in extensions:
        if bot.debug and extension in DISABLED:
            continue

        try:
            await bot.load_extension(extension, package="extensions")
        except Exception as e:
            logger.error('Unable to load extension: "%s" > %s', extension, e)
        else:
            loaded.append(f"extensions{extension}")

    logger.info("Loaded the following extensions: %s", loaded)


async def teardown(bot: core.Bot) -> None:
    extensions: list[str] = [f".{f.stem}" for f in pathlib.Path("extensions").glob("*[a-zA-Z].py")]

    for extension in extensions:
        try:
            await bot.unload_extension(extension, package="extensions")
        except commands.ExtensionNotLoaded:
            pass

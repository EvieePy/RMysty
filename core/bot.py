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

import logging
from typing import TYPE_CHECKING

import discord
import wavelink
from discord.ext import commands

from .config import config


if TYPE_CHECKING:
    from database import Database


logger: logging.Logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, *, database: Database) -> None:
        self.database = database

        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True
        intents.presences = True
        intents.members = True
        super().__init__(intents=intents, command_prefix=config["OPTIONS"]["prefixes"])

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")
        await self.load_extension("extensions")

        uri: str = config["WAVELINK"]["uri"]
        password: str = config["WAVELINK"]["password"]
        
        node: wavelink.Node = wavelink.Node(uri=uri, password=password)
        await wavelink.Pool.connect(nodes=[node], cache_capacity=1000, client=self)

    async def on_ready(self) -> None:
        logger.info("Logged in as %s | %d", self.user, self.user.id)  # type: ignore

    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        logger.info("Successfully connected to %s", payload.node)

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
import logging
from typing import TYPE_CHECKING, Any, Self

import aiohttp
import asyncpg

import core

from .models import *


if TYPE_CHECKING:
    _Pool = asyncpg.Pool[asyncpg.Record]
else:
    _Pool = asyncpg.Pool


__all__ = ("Database",)


logger: logging.Logger = logging.getLogger(__name__)


class Database:
    pool: _Pool

    async def __aenter__(self) -> Self:
        await self.setup()
        return self

    async def __aexit__(self, *args: Any) -> None:
        try:
            await asyncio.wait_for(self.pool.close(), timeout=10)
        except TimeoutError:
            logger.warning("Unable to gracefully shutdown database connection, forcefully continuing.")
        else:
            logger.info("Successfully closed Database connection.")

    async def setup(self) -> None:
        pool: _Pool | None = await asyncpg.create_pool(dsn=core.config["DATABASE"]["dsn"])

        if pool is None:
            raise RuntimeError('Unable to intialise the Database, "create_pool" returned None.')

        self.pool = pool

        try:
            with open("SCHEMA.sql") as fp:
                await self.pool.execute(fp.read())
        except (OSError, AttributeError, asyncpg.PostgresSyntaxError):
            pass

        await self._refresh_colours()
        logger.info("Successfully initialised the Database.")

    async def _refresh_colours(self) -> None:
        logger.info("Refreshing colour database")

        URL: str = "https://unpkg.com/color-name-list@10.25.1/dist/colornames.json"

        async with aiohttp.ClientSession() as session, session.get(URL) as resp:
            try:
                data: list[dict[str, str]] = await resp.json()
            except Exception:
                logger.warning("Unable to refresh colour names in database...")
                return

        query: str = """INSERT INTO colours VALUES ($1, $2) ON CONFLICT DO NOTHING RETURNING *"""
        async with self.pool.acquire() as connection:
            await connection.executemany(query, [(r["name"], r["hex"]) for r in data])

        logger.info("Successfully refreshed colour database")

    async def fetch_colours(self) -> list[ColourRecord]:
        query: str = """SELECT * FROM colours"""

        async with self.pool.acquire() as connection:
            rows: list[ColourRecord] = await connection.fetch(query, record_class=ColourRecord)

        return rows

    async def fetch_colour_name_fuzzy(self, name: str, /, *, threshold: float = 70.0) -> list[ColourRecord]:
        distance: int = int((threshold * len(name)) // 100.0)

        query: str = """
        SELECT * FROM colours
        WHERE levenshtein(name, $1::TEXT) <= $2::INTEGER
        ORDER BY levenshtein(name, $1::TEXT)
        LIMIT 20
        """

        async with self.pool.acquire() as connection:
            rows: list[ColourRecord] = await connection.fetch(query, name, distance, record_class=ColourRecord)

        return rows

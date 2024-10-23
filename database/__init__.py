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

    async def insert_user_paste(self, *, id: str, uid: int, mid: int, vid: int, token: str) -> None:
        query: str = """INSERT INTO pastes(id, uid, mid, vid, token) VALUES($1, $2, $3, $4, $5)"""

        async with self.pool.acquire() as connection:
            await connection.execute(query, id, uid, mid, vid, token)

    async def fetch_user_paste(self, *, id: str, uid: int) -> PasteRecord | None:
        query: str = """SELECT * FROM pastes WHERE id = $1 AND uid = $2"""

        async with self.pool.acquire() as connection:
            row: PasteRecord | None = await connection.fetchrow(query, id, uid, record_class=PasteRecord)

        return row

    async def delete_user_paste(self, *, id: str, uid: int, mid: int) -> None:
        query: str = """DELETE FROM pastes WHERE id = $1 AND uid = $2"""
        second: str = """INSERT INTO paste_blocks(mid) VALUES($1) ON CONFLICT DO NOTHING"""

        async with self.pool.acquire() as connection:
            await connection.execute(query, id, uid)
            await connection.execute(second, mid)

    async def fetch_all_pastes(self) -> list[PasteRecord]:
        query: str = """SELECT * FROM pastes"""

        async with self.pool.acquire() as connection:
            rows: list[PasteRecord] = await connection.fetch(query, record_class=PasteRecord)

        return rows

    async def fetch_all_blocks(self) -> list[PasteBlockRecord]:
        query: str = """SELECT * FROM paste_blocks"""

        async with self.pool.acquire() as connection:
            rows: list[PasteBlockRecord] = await connection.fetch(query, record_class=PasteBlockRecord)

        return rows

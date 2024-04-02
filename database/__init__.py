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
import datetime
import logging
from typing import TYPE_CHECKING, Any, Self

import asyncpg

import core

from .models import *


if TYPE_CHECKING:
    from ..types_.notes import ModeratorNoteData

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

        with open("SCHEMA.sql") as fp:
            await self.pool.execute(fp.read())

        logger.info("Successfully initialised the Database.")

    async def fetch_moderator_notes(self, uid: int, /) -> list[ModeratorNote]:
        query: str = "SELECT * FROM notes WHERE uid = $1"

        async with self.pool.acquire() as connection:
            record: list[asyncpg.Record] = await connection.fetch(query, uid)

        notes: list[ModeratorNote] = [ModeratorNote(data) for data in record]
        return notes

    async def add_moderator_notes(self, data: ModeratorNoteData, /) -> int:
        query: str = """
        INSERT INTO notes (uid, gid, cid, mid, moderator, event, note, additional, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id
        """

        async with self.pool.acquire() as connection:
            row: asyncpg.Record | None = await connection.fetchrow(
                query,
                data["user_id"],
                data["guild_id"],
                data["channel_id"],
                data["message_id"],
                data["moderator_id"],
                data["event"],
                data["note"],
                data["additional"],
                datetime.datetime.now(),
            )

        assert row
        return row["id"]

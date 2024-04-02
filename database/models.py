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

from typing import TYPE_CHECKING

import asyncpg

from core.enums import ModeratorEvent


if TYPE_CHECKING:
    import datetime


__all__ = ("ModeratorNote",)


class ModeratorNote:
    def __init__(self, data: asyncpg.Record) -> None:
        self.id: int = data["id"]
        self.user_id: int = data["uid"]
        self.guild_id: int = data["gid"]
        self.channel_id: int | None = data["cid"]
        self.message_id: int | None = data["mid"]
        self.moderator_id: int = data["moderator"]
        self.event: ModeratorEvent = ModeratorEvent(data["event"])
        self.note: str = data["note"]
        self.additional: str | None = data["additional"]
        self.timestamp: datetime.datetime = data["created_at"]

    def as_dict(self) -> dict[str, str | int | None]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "message_id": self.message_id,
            "moderator_id": self.moderator_id,
            "event": self.event,
            "note": self.note,
            "additional": self.additional,
            "timestamp": self.timestamp.isoformat(),
        }

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

from typing import Any

import asyncpg


__all__ = ("ColourRecord", "PasteBlockRecord", "PasteRecord", "TimezoneRecord")


class ColourRecord(asyncpg.Record):
    name: str
    hex: str

    def __getattr__(self, attr: str) -> Any:
        return self[attr]


class PasteRecord(asyncpg.Record):
    id: str
    uid: int
    mid: int
    vid: int
    token: str

    def __getattr__(self, attr: str) -> Any:
        return self[attr]


class PasteBlockRecord(asyncpg.Record):
    mid: int

    def __getattr__(self, attr: str) -> Any:
        return self[attr]


class TimezoneRecord(asyncpg.Record):
    uid: int
    timezone: str

    def __getattr__(self, attr: str) -> Any:
        return self[attr]

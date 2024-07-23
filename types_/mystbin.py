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

from typing import NotRequired, TypedDict


class MBFileCreate(TypedDict):
    filename: NotRequired[str]
    content: str


class MBFileFetch(TypedDict):
    annotation: str
    charcount: int
    content: str
    filename: str
    loc: int
    parent_id: str


class PasteFetch(TypedDict):
    created_at: str
    expires: str | None
    files: list[MBFileFetch]
    has_password: bool
    id: str
    views: int


class PasteCreate(TypedDict):
    expires: NotRequired[str]
    files: list[MBFileCreate]
    password: NotRequired[str]


class PasteCreateResp(TypedDict):
    created_at: str
    expires: str | None
    id: str
    safety: str

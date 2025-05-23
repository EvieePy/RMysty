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

from typing import TypedDict


class Tokens(TypedDict):
    discord: str


class Database(TypedDict):
    dsn: str


class Options(TypedDict):
    prefixes: str
    logging: int


class Wavelink(TypedDict):
    uri: str
    password: str


class Chii(TypedDict):
    api: str
    web: str


class Pythonista(TypedDict):
    logs: str


class OpenCollective(TypedDict):
    discord_client_id: str
    discord_client_secret: str
    personal_token: str


class Config(TypedDict):
    TOKENS: Tokens
    DATABASE: Database
    OPTIONS: Options
    WAVELINK: Wavelink
    CHII: Chii
    PYTHONISTA: Pythonista
    OPENCOLLECTIVE: OpenCollective

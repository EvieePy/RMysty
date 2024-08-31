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

import json
from typing import TYPE_CHECKING, Any

import discord
from discord import app_commands


if TYPE_CHECKING:
    from types_.translations import Translations


class Translator(app_commands.Translator):
    async def load(self) -> None:
        with open("translations.json", "rb") as fp:
            self.mapping: Translations = json.load(fp)

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext[Any, Any],
    ) -> str | None:
        potential: dict[str, str] = self.mapping.get(str(string).lower(), {})
        translated: str | None = potential.get(locale.value, None)

        return translated

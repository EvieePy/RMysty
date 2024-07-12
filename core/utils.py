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

from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    from types_.codeblocks import CodeBlock


class CodeBlocks:
    def __init__(self, blocks: list[CodeBlock]) -> None:
        self.blocks: list[CodeBlock] = blocks

    @classmethod
    def convert(cls, content: str) -> Self:
        splat: list[str] = content.split("\n")

        in_block: bool = False
        lang: str | None = None
        lines: list[str] = []
        blocks: list[CodeBlock] = []

        for line in splat:
            if in_block and "```" not in line:
                lines.append(line)

            elif not in_block and "```" in line:
                lang = line[line.index("`") :].split()[0].strip("```") or None
                line = line.replace("```", "", 1)

                if "```" in line:
                    data = line.replace("```", "")

                    if data:
                        blocks.append({"language": None, "content": data})

                    lang = None
                    lines = []
                    continue

                in_block = True

            elif in_block and "```" in line:
                if not lines:
                    continue

                joined: str = "\n".join(lines)
                blocks.append({"language": lang, "content": joined})

                lang = None
                lines = []

                in_block = False

        return cls(blocks)

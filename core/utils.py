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

import colorsys
import struct
from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    from types_.codeblocks import CodeBlock
    from types_.colours import Colours


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


class Colour:
    __slots__ = (
        "_code",
        "_hex",
        "_hex_clean",
        "_hls",
        "_hls_coords",
        "_html",
        "_rgb",
        "_rgb_coords",
    )

    def __init__(self, data: Colours) -> None:
        self._code: int = data["code"]
        self._hex: str = data["hex"]
        self._hex_clean: str = data["hex_clean"]
        self._html: str = data["html"]
        self._rgb: tuple[int, int, int] = data["rgb"]
        self._hls: tuple[float, float, float] = data["hls"]
        self._rgb_coords: tuple[float, ...] = data["rgb_coords"]
        self._hls_coords: tuple[float, ...] = data["hls_coords"]

    @property
    def code(self) -> int:
        """Property returning the colour as an integer.

        E.g. `16768256`
        """
        return self._code

    @property
    def hex(self) -> str:
        """Property returning the colour as a hex string.

        E.g. `"0xFFDD00"`
        """
        return self._hex

    @property
    def hex_clean(self) -> str:
        """Property returning the colour as a hex string without any prefix.

        E.g. `"FFDD00"`
        """
        return self._hex_clean

    @property
    def html(self) -> str:
        """Property returning the colour as a hex string with a `#` prefix.

        E.g. `"#FFDD00"`
        """
        return self._html

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Property returning the colour as an RGB tuple of `int`.

        E.g. `(255, 221, 0)`
        """
        return self._rgb

    @property
    def hls(self) -> tuple[float, float, float]:
        """Property returning the colour as an HLS tuple of `float`.

        E.g. `(52, 50, 100)`
        """
        return self._hls

    @property
    def rgb_coords(self) -> tuple[float, ...]:
        """Property returning the colour as an RGB tuple of `float` coordinates.

        E.g. `(1.0, 0.8666666666666667, 0.0)`
        """
        return self._rgb_coords

    @property
    def hls_coords(self) -> tuple[float, ...]:
        """Property returning the colour as an HLS tuple of `float` coordinates.

        E.g. `(0.14444444444444446, 0.5, 1.0)`
        """
        return self._hls_coords

    def __repr__(self) -> str:
        return f"<Colour code={self._code} hex={self._hex} html={self._html}>"

    def __str__(self) -> str:
        return self._hex

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Colour):
            return NotImplemented

        return self._code == __value._code

    def __hash__(self) -> int:
        return hash(self._code)

    def __format__(self, format_spec: str) -> str:
        if format_spec == "html":
            return self._html

        elif format_spec == "rgb":
            return f"rgb{self._rgb}"

        elif format_spec == "hls":
            return f"hls{self._hls}"

        else:
            return str(self)

    def __int__(self) -> int:
        return self._code

    @classmethod
    def from_hex(cls, hex_: str, /) -> Self:
        """Class method to create a Colour object from a hex string.

        A valid hex string can be in either one of the following formats:

        - `"#FFDD00"`
        - `"FFDD00"`
        - `"0xFFDD00"`

        For ints see: `from_int`

        Parameters
        ----------
        hex_: str
            Positional only. The hex string to convert to a Colour object.

        Returns
        -------
        Colour
            The Colour object created from the hex string.
        """
        value: str = hex_.lstrip("#")
        value = value.removeprefix("0x")

        rgb: tuple[int, int, int] = struct.unpack("BBB", bytes.fromhex(value))
        int_: int = int(value, 16)
        html: str = f"#{value}"
        hexa: str = hex(int_)
        rgb_coords: tuple[float, ...] = tuple(c / 255 for c in rgb)

        hue, light, sat = colorsys.rgb_to_hls(*rgb_coords)
        hls: tuple[float, ...] = (round(hue * 360), round(light * 100), round(sat * 100))

        payload: Colours = {
            "code": int_,
            "hex": hexa,
            "hex_clean": value,
            "html": html,
            "rgb": rgb,
            "hls": hls,
            "rgb_coords": rgb_coords,
            "hls_coords": (hue, light, sat),
        }

        return cls(payload)

    @classmethod
    def from_int(cls, code: int, /) -> Self:
        """Class method to create a Colour object from a base-10 or base-16 integer.

        A valid integer can be in either one of the following formats:

        - `16768256`
        - `0xFFDD00`

        For hex strings see: `from_hex`.

        Parameters
        ----------
        code: int
            Positional only. The integer to convert to a Colour object.

        Returns
        -------
        Colour
            The `Colour` object created from the integer.
        """
        hex_: str = f"{code:X}".zfill(6)
        return cls.from_hex(hex_)

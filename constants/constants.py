"""
The MIT License (MIT)

Copyright (c) 2022-Present EvieePy

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from .meta import CONSTANTS


__all__ = ('COLOURS', 'PYTHONISTA')


class COLOURS(CONSTANTS):

    PINK: hex = 0xAB6074
    BLUE: hex = 0x9DB9F6


class PYTHONISTA(CONSTANTS):

    GUILD_ID: int = 490948346773635102
    TWITCHIO_CHANNEL: int = 669115391880069150
    WAVELINK_CHANNEL: int = 739788459006492752
    HELP_CHANNEL: int = 490951172673372195


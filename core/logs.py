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
import logging
from logging.handlers import RotatingFileHandler

from colorama import init, Fore, Back, Style


__all__ = ('Handler', 'Formatter')


init(autoreset=True)
LEVEL_COLOURS = {
    'CRITICAL': {'highlight': Back.RED, 'base': Fore.RED},
    'ERROR': {'highlight': Back.RED, 'base': Fore.RED},
    'WARNING': {'highlight': Back.YELLOW, 'base': Fore.YELLOW},
    'INFO': {'highlight': Back.BLUE, 'base': Fore.LIGHTBLUE_EX},
    'DEBUG': {'highlight': Back.GREEN, 'base': Fore.LIGHTGREEN_EX}
}


class Formatter:

    def colour_format(self, record: logging.LogRecord) -> str:
        colours: dict[str, str] = LEVEL_COLOURS[record.levelname]

        name_back = Back.MAGENTA if record.name.startswith('core') else Back.BLACK
        name_fore = Fore.BLACK if record.name.startswith('core') else Fore.WHITE

        fmt: str = Back.BLACK + \
                   '[{asctime}] ' + \
                   Back.RESET + \
                   colours['highlight'] + \
                   Fore.BLACK + \
                   '[{levelname:<8}]' + \
                   name_back + \
                   name_fore + \
                   ' {name:<20}' + \
                   Back.RESET + \
                   colours['base'] + \
                   ': {message}'

        formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S', style='{')
        return formatter.format(record)

    def format(self, record: logging.LogRecord) -> str:
        fmt: str = '[{asctime}] [{levelname:<8}] {name:<20}: {message}'

        formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S', style='{')
        return formatter.format(record)


class Handler(logging.Handler):

    def __init__(self, level: int) -> None:
        super().__init__()

        self._level = level
        self._formatter: Formatter = Formatter()

        self.rotating = RotatingFileHandler('logs/bot.log', encoding='utf-8', maxBytes=1024 * 1024 * 32)
        self.rotating.setFormatter(self._formatter)

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno >= self._level:
            print(self._formatter.colour_format(record))

        self.rotating.emit(record)
        self.flush()

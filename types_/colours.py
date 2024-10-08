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


class Colours(TypedDict):
    code: int
    hex: str
    hex_clean: str
    html: str
    rgb: tuple[int, int, int]
    hls: tuple[float, float, float]
    rgb_coords: tuple[float, ...]
    hls_coords: tuple[float, ...]


type COORDS_FT = tuple[float, float, float, float]
type COORDS_TT = tuple[float, float]
type COORD_T = tuple[float, ...]
type RGB_T = tuple[int, int, int]

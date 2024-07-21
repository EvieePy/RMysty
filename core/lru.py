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

from collections import deque
from typing import TYPE_CHECKING, Generic, TypeVar, overload


if TYPE_CHECKING:
    from collections.abc import MutableMapping


KT = TypeVar("KT")
VT = TypeVar("VT")
DT = TypeVar("DT")


class LRUCache(Generic[KT, VT]):
    def __init__(self, max_size: int = 100) -> None:
        self._max_size: int = max_size
        self._keys: deque[KT] = deque()
        self._cache: MutableMapping[KT, VT] = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(max_size={self._max_size}, items={len(self._cache)})"

    def __len__(self) -> int:
        return len(self._cache)

    def _rotate(self, key: KT, /) -> VT:
        self._keys.remove(key)
        self._keys.append(key)

        return self._cache[key]

    def __setitem__(self, key: KT, value: VT, /) -> None:
        if key in self._cache:
            self._keys.remove(key)

        elif len(self._cache) == self._max_size:
            removed = self._keys.popleft()
            del self._cache[removed]

        self._cache[key] = value
        self._keys.append(key)

    def __getitem__(self, key: KT, /) -> VT:
        if key not in self._cache:
            raise KeyError(f'The key "{key}" does not exist in {self!r}')

        return self._rotate(key)

    def __delitem__(self, key: KT, /) -> None:
        if key not in self._cache:
            raise KeyError(f'The key "{key}" does not exist in {self!r}')

        self._keys.remove(key)
        del self._cache[key]

    @overload
    def get(self, key: KT, /) -> VT | None: ...

    @overload
    def get(self, key: KT, default: DT, /) -> VT | DT: ...

    def get(self, key: KT, default: DT | None = None, /) -> VT | DT | None:
        if key not in self._cache:
            return default

        return self._rotate(key)

    def clear(self) -> None:
        self._keys = deque()
        self._cache = {}

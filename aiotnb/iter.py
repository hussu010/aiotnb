"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ()

import asyncio
import logging
from typing import (
    TYPE_CHECKING,
    AsyncIterator,
    Awaitable,
    Callable,
    TypeVar,
    Union,
    cast,
)

from .errors import IteratorEmpty
from .utils import coerce_fn

if TYPE_CHECKING:
    from typing import Any, List, Mapping, Optional

    from yarl import URL


_log = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")

Fn = Callable[[T], Union[R, Awaitable[R]]]


class _PaginatedIterator(AsyncIterator[T]):
    _page: asyncio.Queue
    _extra_args: Mapping[str, Any]
    _url: URL
    limit: Optional[int]
    received: int

    async def _next_page(self):
        raise NotImplementedError

    async def next(self) -> T:
        if self._page.empty():
            await self._next_page()

        try:
            return self._page.get_nowait()
        except asyncio.QueueEmpty:
            raise IteratorEmpty()

    async def find(self, check: Fn[T, bool]) -> Optional[T]:
        while True:
            try:
                item = await self.next()

            except IteratorEmpty:
                return None

            if await coerce_fn(check, item):

                return item

    def map(self, fn: Fn[T, R]) -> _PaginatedIteratorMap[R]:
        return _PaginatedIteratorMap(self, fn)

    def filter(self, fn: Fn[T, bool]) -> _PaginatedIteratorFilter[T]:
        return _PaginatedIteratorFilter(self, fn)

    async def flatten(self) -> List[T]:
        return [i async for i in self]

    async def __anext__(self) -> T:
        try:
            return await self.next()

        except IteratorEmpty:
            raise StopAsyncIteration()


class _PaginatedIteratorMap(_PaginatedIterator[T]):
    def __init__(self, iterator: _PaginatedIterator[R], fn: Fn[R, T]):
        self.iter = iterator
        self.fn = fn

    async def next(self) -> T:
        element = await self.iter.next()
        return cast(T, await coerce_fn(self.fn, element))


class _PaginatedIteratorFilter(_PaginatedIterator[T]):
    def __init__(self, iterator: _PaginatedIterator[T], fn: Fn[T, bool]):
        self.iter = iterator
        self.fn = fn

    async def next(self) -> T:
        n = self.iter.next
        f = self.fn

        while True:
            element = await n()

            x = await coerce_fn(f, element)

            if x:
                return element

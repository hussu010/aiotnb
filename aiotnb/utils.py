"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ()

import inspect
import logging
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Mapping, Union

    from typing_extensions import ParamSpec

    P = ParamSpec("P")


try:
    import ujson as json

    _USING_FAST_JSON = True
except ImportError:
    _USING_FAST_JSON = False
    import json


_log = logging.getLogger(__name__)


if not _USING_FAST_JSON:
    _log.warn("ujson not installed, defaulting to json")


# This should be 100% identical to the existing signing method
def message_to_bytes(data: Mapping[str, Any]) -> bytes:
    kwargs: dict[str, Any] = dict(sort_keys=True)

    if not _USING_FAST_JSON:
        kwargs["separators"] = (",", ":")

    return json.dumps(data, **kwargs).encode("utf-8")  # type: ignore


R = TypeVar("R")

# as soon as we have proper ParamSpec support, delete this mess
def partial(fn: Callable[..., R], *args: ..., **kwargs: ...) -> Callable[..., R]:
    def inner(*a: ..., **k: ...) -> R:
        return fn(*args, *a, **kwargs, **k)

    return inner


async def coerce_fn(fn: Union[Callable[P, Awaitable[Any]], Callable[P, Any]], *args: P.args, **kwargs: P.kwargs) -> Any:
    x = fn(*args, **kwargs)

    if inspect.isawaitable(x):
        return await x

    else:
        return x

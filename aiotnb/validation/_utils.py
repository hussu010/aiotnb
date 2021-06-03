"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

from typing import Any, Callable, Optional, TypeVar

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey

__all__ = ("ISO8601UTCTimestamp", "partial")

import datetime
from functools import wraps

from schema import And, Schema, Use

# from typing import Any, Callable, Dict, List, Mapping, Optional, Protocol, Sequence, Type, TypeVar, Union, cast


R = TypeVar("R")

# as soon as we have proper ParamSpec support, delete this mess
def partial(fn: Callable[..., R], *args: ..., **kwargs: ...) -> Callable[..., R]:
    @wraps(fn)
    def inner(*a: ..., **k: ...) -> R:
        return fn(*args, *a, **kwargs, **k)

    return inner


def _parse_iso8601_utc(timestamp: str) -> datetime.datetime:
    """
    Attempts to parse an ISO8601 timestamp.
    """

    return datetime.datetime.fromisoformat(timestamp[:-1])


ISO8601UTCTimestamp: Callable[..., Use] = partial(Use, _parse_iso8601_utc)

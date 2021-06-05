"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("ISO8601UTCTimestamp", "partial", "AccountNumber", "Url")

import datetime
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from schema import And, Schema, Use
from yarl import URL

R = TypeVar("R")

# as soon as we have proper ParamSpec support, delete this mess
def partial(fn: Callable[..., R], *args: ..., **kwargs: ...) -> Callable[..., R]:
    def inner(*a: ..., **k: ...) -> R:
        return fn(*args, *a, **kwargs, **k)

    return inner


def _parse_iso8601_utc(timestamp: str) -> datetime.datetime:
    """
    Attempts to parse an ISO8601 timestamp.
    """

    if timestamp[-1] == "Z":
        timestamp = f"{timestamp[:-1]}+00:00"

    return datetime.datetime.fromisoformat(timestamp)


def _key_from_str(key_str: str) -> VerifyKey:
    return VerifyKey(key_str.encode("utf-8"), encoder=HexEncoder)


def _to_bytes(data: str, *, exact_len: Optional[int]) -> bytes:
    if exact_len is not None and len(data) != exact_len:
        raise ValueError(f"value should be {exact_len} bytes")

    return data.encode("utf-8")


class UrlProtocol(Enum):
    Http = "http"
    Https = "https"


class NodeType(Enum):
    Bank = "BANK"
    PrimaryValidator = "PRIMARY_VALIDATOR"
    Validator = "CONFIRMATION_VALIDATOR"


# Schema models start here

ISO8601UTCTimestamp = And(str, Use(_parse_iso8601_utc))

AccountNumber = And(str, Use(_key_from_str))

BalanceLock = And(str, Use(_to_bytes))

Url = And(str, Use(URL))

Signature = And(str, Use(partial(_to_bytes, exact_len=128)))

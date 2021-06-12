"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = (
    "partial",
    "Key",
    "AccountNumber",
    "Account",
    "BalanceLock",
    "ISO8601UTCTimestamp",
    "Signature",
    "Url",
    "UrlProtocol",
    "NodeType",
)

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from yarl import URL

from ..validation.core import As, Const, Fn, Ignore, Maybe, Schema, Type, Validator

if TYPE_CHECKING:
    from typing import Callable, Optional, TypeVar

    R = TypeVar("R")

# as soon as we have proper ParamSpec support, delete this mess
def partial(fn: Callable[..., R], *args: ..., **kwargs: ...) -> Callable[..., R]:
    def inner(*a: ..., **k: ...) -> R:
        return fn(*args, *a, **kwargs, **k)

    return inner


def _parse_iso8601_utc(timestamp: str) -> datetime:
    """
    Attempts to parse an ISO8601 timestamp.
    """

    if timestamp[-1] == "Z":
        timestamp = f"{timestamp[:-1]}+00:00"

    return datetime.fromisoformat(timestamp)


def _key_from_str(key_str: str) -> VerifyKey:
    return VerifyKey(key_str.encode("utf-8"), encoder=HexEncoder)


def _to_bytes(data: str, *, exact_len: Optional[int]) -> bytes:
    if exact_len is not None and len(data) != exact_len:
        raise ValueError(f"value should be {exact_len} bytes")

    return data.encode("utf-8")


# Schema models start here

Key = partial(As, str)

AccountNumber = Key(_key_from_str)

BalanceLock = Key(_to_bytes)

ISO8601UTCTimestamp = Key(_parse_iso8601_utc)

Signature = Key(partial(_to_bytes, exact_len=128))

Url = Key(URL)


# Helper schemas

AccountSchema = {
    "id": str,
    "created_date": ISO8601UTCTimestamp,
    "modified_date": ISO8601UTCTimestamp,
    "account_number": AccountNumber,
    "trust": Key(float),
}

# Helper classes


# Data models here


class UrlProtocol(Enum):
    """
    Specifies a URL scheme to use for a connection.
    """

    http = "http"
    https = "https"


class NodeType(Enum):
    """
    Differentiates between different types of node.
    """

    bank = "BANK"
    primary_validator = "PRIMARY_VALIDATOR"
    confirmation_validator = "CONFIRMATION_VALIDATOR"


class Account:
    """
    Represents a keypair account on the TNB network.

    Attributes
    ----------
    id: :class:`str`
        A unique identifier representing this account across the network.

    created_date: :class:`~datetime.datetime`
        Date the account was first seen on the network.

    modified_date: :class:`~datetime.datetime`
        Date the account last was modified. This includes balance changes, etc. (TODO)

    account_number: :class:`bytes`
        The public key for the account as hex-encoded bytes.

    trust: :class:`float`
        The trust amount assigned to this account by a given Bank. Can be different across banks.

    bank_id: :class:`bytes`
        The node identifier (NID) of the Bank the account was received from. This is only useful when looking at account trust.
    """

    def __init__(
        self,
        *,
        id: str,
        created_date: datetime,
        modified_date: datetime,
        account_number: VerifyKey,
        trust: float,
        bank_id: bytes,
    ):
        self.id = id
        self.created_date = created_date
        self.modified_date = modified_date
        self.trust = trust
        self.bank_id = bank_id

        self.account_number = account_number.encode(encoder=HexEncoder)
        self._public_key = account_number

    def __repr__(self):
        return f"Account({self.account_number.decode(encoding='utf-8')} [{self.bank_id.decode(encoding='utf-8')}])"

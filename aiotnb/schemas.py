"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = (
    "Key",
    "PublicKey",
    "BalanceLock",
    "Timestamp",
    "Signature",
    "Url",
    "BankConfig",
    "BankDetails",
    "BlockSchema",
    "BankTransactionSchema",
    "ConfirmationBlockSchema",
    "InvalidBlockSchema",
    "AccountSchema",
    "CleanSchema",
    "CrawlSchema",
)

from datetime import datetime
from typing import TYPE_CHECKING

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from yarl import URL

from .common import Account, BankTransaction, Block
from .enums import NodeType, UrlProtocol
from .utils import partial
from .validation import As, Const, Fn, Ignore, Maybe, Schema, Type

if TYPE_CHECKING:
    from typing import Optional


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

PublicKey = Key(_key_from_str)

BalanceLock = Key(_to_bytes)

Timestamp = Key(_parse_iso8601_utc)

Signature = Key(partial(_to_bytes, exact_len=128))

Url = Key(URL)


# Main schemas

BankConfig = Schema(
    {
        "primary_validator": {
            "account_number": PublicKey,
            "ip_address": Url,
            "node_identifier": PublicKey,
            "port": Maybe(int),
            "protocol": Key(UrlProtocol),
            "version": str,
            "default_transaction_fee": int,
            "root_account_file": Url,
            "root_account_file_hash": PublicKey,
            "seed_block_identifier": str,
            "daily_confirmation_rate": Maybe(int),
            "trust": Key(float),
        },
        "account_number": PublicKey,
        "ip_address": Url,
        "node_identifier": PublicKey,
        "port": Maybe(int),
        "protocol": Key(UrlProtocol),
        "version": str,
        "default_transaction_fee": int,
        "node_type": Key(NodeType),
    }
)

BankDetails = Schema(
    {
        "account_number": PublicKey,
        "ip_address": Url,
        "node_identifier": PublicKey,
        "port": Maybe(int),
        "protocol": Key(UrlProtocol),
        "version": str,
        "default_transaction_fee": int,
        "trust": Key(float),
    }
)

BlockSchema = Schema(
    {
        "id": str,
        "created_date": Timestamp,
        "modified_date": Timestamp,
        "balance_key": PublicKey,
        "sender": PublicKey,
        "signature": Signature,
    }
)

BankTransactionSchema = Schema(
    {"id": str, "block": BlockSchema, "amount": int, "fee": Key(NodeType), "memo": str, "recipient": PublicKey}
)

ConfirmationBlockSchema = Schema(
    {
        "id": str,
        "created_date": Timestamp,
        "modified_date": Timestamp,
        "block_identifier": PublicKey,
        "block": str,
        "validator": str,
    }
)

InvalidBlockSchema = Schema(
    {
        "id": str,
        "created_date": Timestamp,
        "modified_date": Timestamp,
        "block_identifier": PublicKey,
        "block": str,
        "confirmation_validator": str,
        "primary_validator": str,
    }
)

AccountSchema = Schema(
    {
        "id": str,
        "created_date": Timestamp,
        "modified_date": Timestamp,
        "account_number": PublicKey,
        "trust": Key(float),
    }
)


CleanSchema = Schema(
    {
        "clean_last_completed": Maybe(Timestamp),
        "clean_status": Maybe(str),
        "ip_address": Url,
        "port": Maybe(int),
        "protocol": Key(UrlProtocol),
    }
)

CrawlSchema = Schema(
    {
        "crawl_last_completed": Maybe(Timestamp),
        "crawl_status": Maybe(str),
        "ip_address": Url,
        "port": Maybe(int),
        "protocol": Key(UrlProtocol),
    }
)

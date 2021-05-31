"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

__all__ = ("ISO8601UTCTimestamp", "UserAccount")

import datetime
from functools import partial

from schema import And, Schema, Use


def parse_iso8601_utc(timestamp: str) -> datetime.datetime:
    """
    Attempts to parse an ISO8601 timestamp.
    """

    return datetime.datetime.fromisoformat(timestamp[:-1])


ISO8601UTCTimestamp = partial(Use, parse_iso8601_utc)


account_schema = Schema(
    {
        "id": str,
        "created_date": ISO8601UTCTimestamp(error="created_date not valid timestamp"),
        "modified_date": ISO8601UTCTimestamp(error="modified_date not valid timestamp"),
        "account_number": str,
        "trust": And(str, Use(float, error="trust not a float value")),
    }
)


class Account:
    def __init__(
        self,
        id: str,
        created_date: datetime.datetime,
        modified_date: datetime.datetime,
        account_number: str,
        trust: float,
    ):
        self.id = id
        self.created_date = created_date
        self.modified_date = modified_date
        self.account_number = account_number
        self.trust = trust

    def __str__(self):
        return f"<UserAccount(number={self.account_number}, trust={self.trust})>"

    __repr__ = __str__


UserAccount = partial(And, account_schema, Use(lambda s: Account(**s)))

"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("validate_with", "BankConfig", "AccountList", "transform", "core")

from functools import wraps
from typing import TYPE_CHECKING

from aiotnb.exceptions import ValidatorException, ValidatorFailed

from ..models.helpers import AccountNumber, Key, NodeType, Url, UrlProtocol
from .core import As, Const, Fn, Ignore, Maybe, Schema, Type, Validator

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Mapping, TypeVar

    from typing_extensions import ParamSpec

    _A = ParamSpec("_A")
    _M = TypeVar("_M", bound=Mapping[str, Any])


def transform(schema: Validator, data: Any) -> Any:
    is_ok = schema.validate(data)

    if not is_ok:
        raise ValidatorFailed(f"Had schema: {schema!r}\nHad data: {data!r}")

    return schema.transform(data)


def validate_with(schema: Validator):
    def deco(fn: Callable[_A, Awaitable[_M]]) -> Callable[_A, Awaitable[Any]]:
        @wraps(fn)
        async def inner(*args: _A.args, **kwargs: _A.kwargs) -> Any:
            result = await fn(*args, **kwargs)

            return transform(schema, result)

        return inner

    return deco


# Schema helpers


# Actual validator schemas

BankConfig = Schema(
    {
        "primary_validator": dict,
        "account_number": AccountNumber,
        "ip_address": Url,
        "node_identifier": AccountNumber,
        "port": Maybe(int),
        "protocol": Key(UrlProtocol),
        "version": str,
        "default_transaction_fee": int,
        "node_type": Key(NodeType),
    }
)

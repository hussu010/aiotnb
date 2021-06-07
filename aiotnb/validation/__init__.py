"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("validate_with", "ISO8601UTCTimestamp")

from functools import wraps
from typing import TYPE_CHECKING

from schema import And, Optional, Or, Schema, SchemaError, Use

from aiotnb.exceptions import ValidatorException

from ._utils import (
    AccountNumber,
    BalanceLock,
    ISO8601UTCTimestamp,
    OptionalVal,
    Signature,
    Url,
    partial,
)

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Mapping, TypeVar

    from typing_extensions import ParamSpec

    _A = ParamSpec("_A")
    _M = TypeVar("_M", bound=Mapping[str, Any])


def validate_with(schema: Schema):
    def deco(fn: Callable[_A, Awaitable[_M]]) -> Callable[_A, Awaitable[Any]]:
        @wraps(fn)
        async def inner(*args: _A.args, **kwargs: _A.kwargs) -> Any:
            result = await fn(*args, **kwargs)

            try:
                transformed_result = schema.validate(result)

            except SchemaError as e:
                raise ValidatorException(result, e) from e

            return transformed_result

        return inner

    return deco

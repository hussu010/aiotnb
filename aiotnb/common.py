"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("Account", "PaginatedResponse")

import logging
from enum import Enum
from typing import TYPE_CHECKING, AsyncIterator, TypeVar, cast

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from yarl import URL

from . import validation
from .errors import IteratorEmpty
from .http import HTTPClient
from .schemas import PAGINATOR_BASE

if TYPE_CHECKING:
    from datetime import datetime
    from typing import Any, List, Mapping


_log = logging.getLogger(__name__)

# Common classes


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


T = TypeVar("T")


class PaginatedResponse(AsyncIterator[T]):
    """
    An iterator over n-many pages of data from the API. (TODO)

    .. admonition:: Supported Operations

        .. describe:: async for x in y
            Asynchronously iterate over the contents of the iterator.

    """

    def __init__(
        self, _client: HTTPClient, result_schema: Mapping[str, Any], type_: T, url: URL, *args: Any, **kwargs: Any
    ):
        self._client = _client
        self.result_type = type_

        # Paginator args
        self.limit = kwargs.pop("limit", 0)

        # HTTP args
        self._request_params = kwargs.pop("params", {})

        # Validator extra args
        self._validator_args = kwargs.pop("validator_args", {})

        schema = PAGINATOR_BASE
        schema["results"] = [validation.As(result_schema, type_, **kwargs.pop("response_as_args", {}))]

        self.schema = validation.Schema(schema).resolve()

        self._num_records = 0
        self._total = 0
        self._count = 0
        self._next = url
        self._previous = None
        self._current = 0

        self._data: List[T] = []

    async def next(self) -> T:
        """
        Step forward one item if possible. (TODO)
        """
        if self._next is None and self._current >= self._count or (self.limit != 0 and self._num_records == self.limit):
            raise IteratorEmpty()

        def _data():
            data = self._data[self._current]
            self._current += 1
            self._num_records += 1
            return data

        if self._current < self._count:
            return _data()

        else:
            if self._request_params:
                kwargs = {"params": self._request_params}
                self._request_params = None
            else:
                kwargs = {}

            data = await self._client.request(("GET", self._next), **kwargs)

            with validation.ArgsManager.temp(self.result_type, **self._validator_args):
                result = validation.transform(self.schema, data)

            self._current = 0
            self._total = result["count"]
            self._next = result["next"]
            self._previous = result["previous"]
            self._data = result["results"]
            self._count = len(self._data)

            if self._current < self._count:
                return _data()

            raise IteratorEmpty()

    async def previous(self) -> T:
        """
        Step backward one item if possible. (TODO)
        """
        if self._previous is None and self._current < 0 or (self.limit != 0 and self._num_records == self.limit):
            raise IteratorEmpty()

        def _data():
            data = self._data[self._current]
            self._current -= 1
            self._num_records += 1
            return data

        if 0 <= self._current <= (self._count - 1):
            return _data()

        else:

            if self._request_params:
                kwargs = {"params": self._request_params}
                self._request_params = None
            else:
                kwargs = {}

            data = await self._client.request(("GET", cast(URL, self._previous)), **kwargs)

            with validation.ArgsManager.temp(self.result_type, **self._validator_args):
                result = validation.transform(self.schema, data)

            self._total = result["count"]
            self._next = result["next"]
            self._previous = result["previous"]
            self._data = result["results"]
            self._count = len(self._data)
            self._current = self._count - 1

            if 0 <= self._current <= (self._count - 1):
                return _data()

            raise IteratorEmpty()

    async def flatten(self) -> List[T]:
        """
        Collect the entire iterator into a single list. (TODO)
        """
        return [t async for t in self]

    async def __anext__(self) -> T:
        try:
            return await self.next()

        except IteratorEmpty:
            raise StopAsyncIteration()

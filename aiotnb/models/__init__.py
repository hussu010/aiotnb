"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("Bank", "ConfirmationValidator", "Validator", "AccountListOrder")

import logging
from enum import Enum
from typing import TYPE_CHECKING, AsyncIterator, TypeVar, cast

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from yarl import URL

from ..exceptions import IteratorEmpty
from ..http import HTTPClient, HTTPMethod, Route
from ..validation import BankConfig
from ..validation import core as vcore
from ..validation import transform
from .helpers import Account, AccountSchema, NodeType, UrlProtocol

if TYPE_CHECKING:
    from typing import Any, List, Mapping, Optional


_log = logging.getLogger(__name__)


# User-facing objects that aren't data models


class AccountListOrder(Enum):
    created_asc = "created_date"
    created_desc = "-created_date"
    modified_asc = "modified_date"
    modified_desc = "-modified_date"
    id_asc = "id"
    id_desc = "-id"
    number_asc = "account_number"
    number_desc = "-account_number"
    trust_asc = "trust"
    trust_desc = "-trust"


class Bank:
    """
    Represents a Bank node on the TNB network. This object should not be manually created, instead use :func:`.connect_to_bank`.


    Attributes
    ----------
    account_number: :class:`bytes`
        The account number of the Bank node as hex-encoded bytes.

    node_identifier: :class:`bytes`
        The node identifier (NID) of the Bank node as hex-encoded bytes.

    version: :class:`str`
        The version identifier of the node.

    transaction_fee: :class:`int`
        The fee this node charges for handling transactions.

    node_type: :class:`.NodeType`
        An enum value representing the type of node. Will always be ``NodeType.Bank``.

    ip_address: :class:`str`
        The IP address of this Bank node.

    port: :class:`int`
        The port number this node accepts connections on.

    protocol: :class:`.UrlProtocol`
        An enum value representing the scheme this node handles connections with.

    address: :class:`~yarl.URL`
        The fully-formed URL for this node.

    primary_validator: Mapping[:class:`str`, Any]
        The primary Validator node this Bank node uses. For now this is just the raw response data.

    """

    def __init__(
        self,
        _client: HTTPClient,
        *,
        account_number: VerifyKey,
        ip_address: URL,
        node_identifier: VerifyKey,
        port: Optional[int],
        protocol: UrlProtocol,
        version: str,
        default_transaction_fee: int,
        node_type: NodeType,
        primary_validator: Mapping[str, Any],
    ):
        self.account_number = account_number.encode(encoder=HexEncoder)
        self._account_number = account_number

        self.node_identifier = node_identifier.encode(encoder=HexEncoder)
        self._node_identifier = node_identifier

        self.version = version  # TODO: int-tuple for version
        self.transaction_fee = default_transaction_fee

        self.node_type = node_type
        assert (
            node_type == NodeType.bank
        ), f"attempt to initiate a Bank object with non-bank node data: {node_type.value}"

        self.ip_address = str(ip_address)
        self.port = port
        self.protocol = protocol

        self.address = URL.build(
            scheme=protocol.value,
            host=self.ip_address,
            port=port or 80,
        )

        self.primary_validator = primary_validator

        self._client = _client

    async def _request(self, route: Route, **kwargs):
        return await self._client.request(route.resolve(self.address), **kwargs)

    # Endpoint methods

    async def fetch_accounts(
        self,
        *,
        offset: int = 0,
        limit: int = 0,
        ordering: AccountListOrder = AccountListOrder.created_asc,
        page_limit: int = 50,
    ):
        payload = {"offset": offset, "limit": page_limit, "ordering": ordering.value}

        _, url = Route(HTTPMethod.get, "accounts").resolve(self.address)

        paginator = PaginatedResponse(
            self._client,
            AccountSchema,
            Account,
            url,
            limit=limit,
            extra=dict(bank_id=self.node_identifier),
            filter=lambda a, d, **b: a(**d, **b),
            params=payload,
        )

        return paginator


class ConfirmationValidator:
    """
    Object representing a Confirmation Validator on the TNB network.

    """

    pass


class Validator:
    """
    Object representing a Validator on the TNB network.

    """

    pass


T = TypeVar("T")

PAGINATOR_BASE = {
    "count": int,
    "next": vcore.Maybe(helpers.Url),
    "previous": vcore.Maybe(helpers.Url),
    "results": None,
}


class PaginatedResponse(AsyncIterator[T]):
    def __init__(
        self, _client: HTTPClient, result_schema: Mapping[str, Any], type_: T, url: URL, *args: Any, **kwargs: Any
    ):
        self._client = _client
        self.result_type = type_
        self.extra_args = kwargs.pop("extra")

        self.limit = kwargs.pop("limit", 0)

        self._params = kwargs.pop("params", {})
        self._offset = 0

        schema = PAGINATOR_BASE
        schema["results"] = [vcore.As(result_schema, type_, *args, **kwargs)]

        self.schema = vcore.Schema(schema).resolve()

        self._num_records = 0
        self._total = 0
        self._count = 0
        self._next = url
        self._previous = None

        self._data: List[T] = []

        self._current = 0

    async def next(self) -> T:
        if self._next is None and self._current >= self._count or (self.limit != 0 and self._num_records == self.limit):
            raise IteratorEmpty()

        def check():
            if self._current < self._count:
                data = self._data[self._current]
                self._current += 1
                self._num_records += 1
                return data

        tmp = check()
        if tmp:
            return tmp

        else:
            kwargs = {}

            if self._params:
                self._params["offset"] = self._offset
                kwargs["params"] = self._params
                self._params = None
            else:
                kwargs["params"] = {"offset": self._offset}

            data = await self._client.request(("GET", self._next), **kwargs)

            with vcore.ArgsManager.temp(self.result_type, **self.extra_args):
                result = transform(self.schema, data)

            self._current = 0
            self._total = result["count"]
            self._next = result["next"]
            self._previous = result["previous"]
            self._data = result["results"]
            self._count = len(self._data)

            self._offset = self._next.query["offset"] if self._next else 0

            tmp = check()
            if tmp:
                return tmp

            raise IteratorEmpty()

    async def previous(self) -> T:
        if self._previous is None and self._current < 0 or (self.limit != 0 and self._num_records == self.limit):
            raise IteratorEmpty()

        def check():
            if 0 <= self._current <= (self._count - 1):
                data = self._data[self._current]
                self._current -= 1
                self._num_records += 1
                return data

        tmp = check()
        if tmp:
            return tmp

        else:

            kwargs = {}

            if self._params:
                self._params["offset"] = self._offset
                kwargs["params"] = self._params
                self._params = None
            else:
                kwargs["params"] = {"offset": self._offset}

            data = await self._client.request(("GET", cast(URL, self._previous)), **kwargs)

            with vcore.ArgsManager.temp(self.result_type, **self.extra_args):
                result = transform(self.schema, data)

            self._total = result["count"]
            self._next = result["next"]
            self._previous = result["previous"]
            self._data = result["results"]
            self._count = len(self._data)
            self._current = self._count - 1

            self._offset = self._previous.query["offset"] if self._previous else 0

            tmp = check()
            if tmp:
                return tmp

            raise IteratorEmpty()

    async def flatten(self) -> List[T]:
        return [t async for t in self]

    async def __anext__(self) -> T:
        try:
            return await self.next()

        except IteratorEmpty:
            raise StopAsyncIteration()

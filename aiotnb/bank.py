"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("Bank",)

import logging
from typing import TYPE_CHECKING

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from yarl import URL

from .common import Account, PaginatedResponse
from .enums import AccountOrder, NodeType, UrlProtocol
from .http import HTTPClient, HTTPMethod, Route
from .schemas import AccountSchema
from .validation import transform

if TYPE_CHECKING:
    from typing import Any, Mapping, Optional


_log = logging.getLogger(__name__)


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
        ordering: AccountOrder = AccountOrder.created_asc,
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
            params=payload,
            validator_args=dict(bank_id=self.node_identifier),
            response_as_args=dict(unpack_args=True),
        )

        return paginator

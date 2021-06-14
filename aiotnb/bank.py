"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("Bank",)

import logging
from typing import TYPE_CHECKING, Union, cast

from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey
from yarl import URL

from .common import Account, BankTransaction, Block, PaginatedResponse
from .enums import AccountOrder, NodeType, UrlProtocol
from .http import HTTPClient, HTTPMethod, Route
from .keypair import AnyPubKey, LocalAccount, key_as_str
from .schemas import AccountSchema, BankTransactionSchema
from .utils import message_to_bytes
from .validation import ArgsManager, transform

if TYPE_CHECKING:
    from typing import Any, Mapping, Optional


_log = logging.getLogger(__name__)


class Bank:
    """
    Represents a Bank node on the TNB network. This object should not be manually created, instead use :func:`.connect_to_bank`.


    Attributes
    ----------
    account_number: :class:`str`
        The account this bank uses to receive transaction fees.

    account_number_bytes: :class:`bytes`
        The account number of the bank node as hex-encoded bytes.

    node_identifier: :class:`str`
        The node identifier (NID) of this bank node.

    node_identifier_bytes: :class:`bytes`
        The NID of this bank node as hex-encoded bytes.

    version: :class:`str`
        The version identifier of this node.

    transaction_fee: :class:`int`
        The fee this node charges for handling transactions.

    node_type: :class:`.NodeType`
        An enum value representing the type of node. Will always be ``NodeType.bank``.

    ip_address: :class:`str`
        The IP address of this bank node.

    port: :class:`int`
        The port number this node accepts connections on.

    protocol: :class:`.UrlProtocol`
        An enum value representing the scheme this node handles connections with.

    address: :class:`~yarl.URL`
        The fully-formed URL for this node.

    primary_validator: Mapping[:class:`str`, Any]
        The primary balidator node this bank node uses. For now this is just the raw response data.

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
        self.account_number_bytes = account_number.encode(encoder=HexEncoder)
        self.account_number = self.account_number_bytes.decode("utf-8")
        self._account_number = account_number

        self.node_identifier_bytes = node_identifier.encode(encoder=HexEncoder)
        self.node_identifier = self.node_identifier_bytes.decode("utf-8")
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
        )

        return paginator

    async def set_account_trust(self, account_number: AnyPubKey, trust: float, node_keypair: LocalAccount) -> Account:
        payload = {"trust": trust}

        payload_data = message_to_bytes(payload)
        signed = node_keypair.sign_message(payload_data)

        payload = {
            "message": payload,
            "node_identifier": node_keypair.account_number,
            "signature": signed.signature.decode("utf-8"),
        }

        route = Route(HTTPMethod.patch, "accounts/{account_number}", account_number=key_as_str(account_number))

        result = await self._request(route, json=payload)

        with ArgsManager.temp(Account, bank_id=self.node_identifier):
            account = transform(AccountSchema, result)

        return account

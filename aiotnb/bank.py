"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

from enum import Enum

__all__ = ("Bank",)

import logging
from typing import TYPE_CHECKING

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from yarl import URL

from .common import Account, BankTransaction, PaginatedResponse
from .enums import AccountOrder, NodeType, TransactionOrder, UrlProtocol
from .http import HTTPMethod, Route
from .keypair import AnyPubKey, LocalAccount, key_as_str
from .schemas import AccountSchema, BankTransactionSchema
from .utils import message_to_bytes
from .validation import ArgsManager, transform

if TYPE_CHECKING:
    from typing import Any, Mapping, Optional

    from .state import InternalState


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
        state: InternalState,
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

        self._state = state

    async def _request(self, route: Route, **kwargs):
        return await self._state.client.request(route.resolve(self.address), **kwargs)

    # Endpoint methods

    async def fetch_accounts(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        ordering: AccountOrder = AccountOrder.created,
        page_limit: int = 100,
    ):
        """
        Request a list of accounts a bank is aware of.

        Returns an async iterator over ``Account`` objects.

        .. seealso::

            For details about the iterator, see :class:`AsyncIterator`.

        Parameters
        ----------
        offset: :class:`int`
            Determines how many accounts to skip before returning data.

        limit: :class:`int`
            Determines the maximum number of accounts to return.

        ordering: :class:`.AccountOrder`
            Determines in what order the results are returned.

        page_limit: :class:`int`
            Determines how many results to return per page, defaults to 100. You should not have to adjust this.

        Raises
        ------
        ~aiotnb.Forbidden
            The server did not allow access to this endpoint.

        ~aiotnb.NotFound
            The endpoint URL was not present on the server.

        ~aiotnb.NetworkServerError
            The server encountered an error.

        ~aiotnb.HTTPException
            Something else went wrong.

        Yields
        ------
        :class:`.Account`
            The account information.

        """
        payload = {"offset": offset, "limit": page_limit, "ordering": ordering.value}

        _, url = Route(HTTPMethod.get, "accounts").resolve(self.address)

        paginator: PaginatedResponse[Account] = PaginatedResponse(
            self._state,
            AccountSchema,
            url,
            limit=limit,
            params=payload,
            extra=dict(bank_id=self.node_identifier),
        )

        return paginator

    async def set_account_trust(self, account_number: AnyPubKey, trust: float, node_keypair: LocalAccount) -> Account:
        """
        Update the trust measure this bank has for a given account. You need the bank's signing key to do this.

        Parameters
        ----------
        account_number: Union[:class:`~nacl.signing.VerifyKey`, :class:`bytes`, :class:`str`]
            The account number to edit trust for. Accepts a variety of types.

        trust: :class:`float`
            The new trust value for the account.

        node_keypair: :class:`.LocalAccount`
            The keypair corresponding to the specific bank.

            .. note::

                This must be the **bank's** public key and the **bank's** private key.

        Raises
        ------
        ~aiotnb.Unauthorized
            The server did not accept the message signature.

        ~aiotnb.Forbidden
            The server did not allow access to this endpoint.

        ~aiotnb.NotFound
            The endpoint URL was not present on the server.

        ~aiotnb.NetworkServerError
            The server encountered an error.

        ~aiotnb.HTTPException
            Something else went wrong.

        Returns
        -------
        :class:`.Account`
            The new account with trust updated.
        """
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

    async def fetch_transactions(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        ordering: TransactionOrder = TransactionOrder.block_created,
        page_limit: int = 100,
        **kwargs,
    ):
        """
        Request a list of transactions a bank is aware of.

        Returns an async iterator over ``BankTransaction`` objects.

        .. seealso::

            For details about the iterator, see :class:`AsyncIterator`.

        Parameters
        ----------
        offset: :class:`int`
            Determines how many accounts to skip before returning data.

        limit: :class:`int`
            Determines the maximum number of accounts to return.

        ordering: :class:`.AccountOrder`
            Determines in what order the results are returned.

        page_limit: :class:`int`
            Determines how many results to return per page, defaults to 100. You should not have to adjust this.

        filter_sender: Optional[:class:`str`]
            An account number as a string. Filters results based on sender account number

        filter_fee: Optional[Union[:class:`NodeType`, :class:`str`]]
            A fee type as a string or ``NodeType``. Filters results based on fee.

        filter_recipient: Optional[:class:`str`]
            An account number as a string. Filters results based on recipient account number

        Raises
        ------
        ~aiotnb.Forbidden
            The server did not allow access to this endpoint.

        ~aiotnb.NotFound
            The endpoint URL was not present on the server.

        ~aiotnb.NetworkServerError
            The server encountered an error.

        ~aiotnb.HTTPException
            Something else went wrong.

        Yields
        ------
        :class:`.BankTransaction`
            The transaction details.
        """
        payload = {"offset": offset, "limit": page_limit, "ordering": ordering.value}

        if kwargs.get("filter_sender") is not None:
            payload["block__sender"] = kwargs.pop("filter_sender")

        if kwargs.get("filter_fee") is not None:
            fee = kwargs.pop("filter_fee")
            if isinstance(fee, Enum):
                fee = fee.value

            payload["fee"] = fee

        if kwargs.get("filter_recipient") is not None:
            payload["recipient"] = kwargs.pop("filter_recipient")

        if kwargs.get("filter_account") is not None:
            payload["account_number"] = kwargs.pop("filter_account")

        _, url = Route(HTTPMethod.get, "bank_transactions").resolve(self.address)

        paginator: PaginatedResponse[BankTransaction] = PaginatedResponse(
            self._state,
            BankTransactionSchema,
            url,
            limit=limit,
            params=payload,
            extra=dict(bank_id=self.node_identifier),
        )

        return paginator

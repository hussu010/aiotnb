"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("Bank",)

import asyncio
import logging
from enum import Enum
from typing import TYPE_CHECKING

from nacl.encoding import HexEncoder
from yarl import URL

from .common import Account, BankTransaction, Block, PaginatedResponse
from .enums import (
    AccountOrder,
    BankOrder,
    BlockOrder,
    NodeType,
    TransactionOrder,
    UrlProtocol,
)
from .errors import ValidatorFailed
from .http import HTTPMethod, Route
from .keypair import key_as_str
from .schemas import (
    AccountSchema,
    BankConfig,
    BankDetails,
    BankTransactionSchema,
    BlockSchema,
)
from .utils import message_to_bytes

if TYPE_CHECKING:
    from typing import Any, Optional

    from nacl.signing import VerifyKey

    from .keypair import AnyPubKey, LocalAccount
    from .payment import TransactionBlock
    from .state import InternalState
    from .validator import Validator


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

    def __eq__(self, other):
        if isinstance(other, Bank):
            return self.node_identifier == other.node_identifier
        raise NotImplemented

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
        primary_validator: Optional[Validator],
    ):
        self.node_type = node_type
        assert (
            node_type == NodeType.bank
        ), f"attempt to initiate a Bank object with non-bank node data: {node_type.value}"

        self.node_identifier_bytes = node_identifier.encode(encoder=HexEncoder)
        self.node_identifier = self.node_identifier_bytes.decode("utf-8")
        self._node_identifier = node_identifier

        self._primary_validator = primary_validator

        self._state = state

        self._update(
            account_number=account_number,
            ip_address=ip_address,
            port=port,
            protocol=protocol,
            version=version,
            default_transaction_fee=default_transaction_fee,
            primary_validator=primary_validator,
        )

    def _update(
        self,
        *,
        account_number: VerifyKey,
        ip_address: URL,
        port: Optional[int] = None,
        protocol: UrlProtocol,
        version: str,
        default_transaction_fee: int,
        primary_validator: Optional[Validator] = None,
        **kwargs,
    ):

        node_type = kwargs.get("node_type")
        if node_type is not None:
            assert (
                node_type == NodeType.bank
            ), f"attempt to initiate a Bank object with non-bank node data: {node_type.value}"

        self.account_number_bytes = account_number.encode(encoder=HexEncoder)
        self.account_number = self.account_number_bytes.decode("utf-8")
        self._account_number = account_number

        self.version = version  # TODO: int-tuple for version
        self.transaction_fee = default_transaction_fee

        self.ip_address = str(ip_address)
        self.port = port
        self.protocol = protocol

        self.address = URL.build(
            scheme=protocol.value,
            host=self.ip_address,
            port=port or 80,
        )

        self._primary_validator = primary_validator

    @property
    def primary_validator(self):
        if self._primary_validator is None:
            # Using ensure_future here instead of create_task to allow for Python < 3.7
            return asyncio.ensure_future(self._get_primary_validator()).result()

        else:
            return self._primary_validator

    async def _get_primary_validator(self):
        data = await self._request(Route(HTTPMethod.get, "config"))

        if BankConfig.validate(data):
            self._primary_validator = self._state.create_validator(data["primary_validator"])

        else:
            raise ValidatorFailed(f"got data: {data!r}")

        return self._primary_validator

    def _request(self, route: Route, **kwargs):
        return self._state.client.request(route.resolve(self.address), **kwargs)

    # Endpoint methods

    async def fetch_accounts(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        ordering: AccountOrder = AccountOrder.created,
        page_limit: int = 100,
    ) -> PaginatedResponse[Account]:
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

        paginator = PaginatedResponse(
            self._state,
            AccountSchema,
            Account,
            url,
            limit=limit,
            params=payload,
            extra=dict(bank_id=self.node_identifier),
        )

        return paginator

    async def set_account_trust(self, account_number: AnyPubKey, trust: float, node_keypair: LocalAccount) -> Account:
        """
        Update the trust measure this bank has for a given account. You need this bank's signing key to do this.

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

        data = AccountSchema.transform(result)
        account = self._state.create_account(dict(**data, bank_id=self.node_identifier))

        return account

    async def fetch_transactions(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        ordering: TransactionOrder = TransactionOrder.block_created,
        page_limit: int = 100,
        **kwargs: Any,
    ) -> PaginatedResponse[BankTransaction]:
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

        filter_sender: Optional[:ref:`AnyPubKey`]
            An account number. Filters results based on sender account number

        filter_fee: Optional[Union[:class:`NodeType`, :class:`str`]]
            A fee type as a string or ``NodeType``. Filters results based on fee.

        filter_recipient: Optional[:ref:`AnyPubKey`]
            An account number. Filters results based on recipient account number

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
            payload["block__sender"] = key_as_str(kwargs.pop("filter_sender"))

        if kwargs.get("filter_fee") is not None:
            fee = kwargs.pop("filter_fee")
            if isinstance(fee, Enum):
                fee = fee.value

            payload["fee"] = fee

        if kwargs.get("filter_recipient") is not None:
            payload["recipient"] = key_as_str(kwargs.pop("filter_recipient"))

        if kwargs.get("filter_account") is not None:
            payload["account_number"] = key_as_str(kwargs.pop("filter_account"))

        _, url = Route(HTTPMethod.get, "bank_transactions").resolve(self.address)

        paginator = PaginatedResponse(
            self._state,
            BankTransactionSchema,
            BankTransaction,
            url,
            limit=limit,
            params=payload,
            extra=dict(bank_id=self.node_identifier),
        )

        return paginator

    async def fetch_banks(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        ordering: BankOrder = BankOrder.trust_desc,
        page_limit: int = 100,
    ) -> PaginatedResponse[Bank]:
        """
        Request a list of other banks a bank is connected is aware of.

        Returns an async iterator over ``Bank`` objects.

        .. seealso::

            For details about the iterator, see :class:`AsyncIterator`.

        Parameters
        ----------
        offset: :class:`int`
            Determines how many accounts to skip before returning data.

        limit: :class:`int`
            Determines the maximum number of accounts to return.

        ordering: :class:`.BankOrder`
            Determines in what order the results are returned.

        page_limit: :class:`int`
            Determines how many results to return per page, max of 100. You should not have to adjust this.

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
        :class:`.Bank`
            Bank object.
        """
        payload = {"offset": offset, "limit": page_limit, "ordering": ordering.value}

        _, url = Route(HTTPMethod.get, "banks").resolve(self.address)

        paginator = PaginatedResponse(
            self._state,
            BankDetails,
            Bank,
            url,
            limit=limit,
            params=payload,
        )

        return paginator

    async def set_bank_trust(self, node_identifier: AnyPubKey, trust: float, node_keypair: LocalAccount) -> Bank:
        """
        Update the trust measure this bank has for a given bank. You need this bank's signing key to do this.

        Parameters
        ----------
        node_identifier: Union[:class:`~nacl.signing.VerifyKey`, :class:`bytes`, :class:`str`]
            The node identifier (NID) of the bank to edit trust for. Accepts a variety of types.

        trust: :class:`float`
            The new trust value for the bank.

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
        :class:`.Bank`
            The new bank with trust updated.
        """
        payload = {"trust": trust}

        payload_data = message_to_bytes(payload)
        signed = node_keypair.sign_message(payload_data)

        payload = {
            "message": payload,
            "node_identifier": node_keypair.account_number,
            "signature": signed.signature.decode("utf-8"),
        }

        route = Route(HTTPMethod.patch, "banks/{node_identifier}", node_identifier=key_as_str(node_identifier))

        result = await self._request(route, json=payload)

        new_data = AccountSchema.transform(result)
        bank = self._state.create_bank(new_data)

        return bank

    async def fetch_blocks(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        ordering: BlockOrder = BlockOrder.created,
        page_limit: int = 100,
        **kwargs: Any,
    ) -> PaginatedResponse[Block]:
        """
        Request a list of blocks a bank is aware of.

        Returns an async iterator over ``Block`` objects.

        .. seealso::

            For details about the iterator, see :class:`AsyncIterator`.

        Parameters
        ----------
        offset: :class:`int`
            Determines how many accounts to skip before returning data.

        limit: :class:`int`
            Determines the maximum number of accounts to return.

        ordering: :class:`.BlockOrder`
            Determines in what order the results are returned.

        page_limit: :class:`int`
            Determines how many results to return per page, defaults to 100. You should not have to adjust this.

        filter_sender: Optional[:ref:`AnyPubKey`]
            An account number as a string. Filters results based on sender account number

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
        :class:`.Block`
            Block information.
        """
        payload = {"offset": offset, "limit": page_limit, "ordering": ordering.value}

        if kwargs.get("filter_sender") is not None:
            payload["sender"] = key_as_str(kwargs.pop("filter_sender"))

        _, url = Route(HTTPMethod.get, "blocks").resolve(self.address)

        paginator = PaginatedResponse(self._state, BlockSchema, Block, url, limit=limit, params=payload)

        return paginator

    async def _add_block(self, block: TransactionBlock) -> Block:
        """
        Send a new block of transactions to a bank to be verified and added to the chain.

        Parameters
        ----------
        block: :class:`TransactionBlock`
            The transaction data to add to the chain.

        Raises
        ------
        ~aiotnb.Unauthorized
            The server did not accept the block signature.

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
        :class:`.Block`
            The new block that was added.
        """
        payload = block.finalize()

        route = Route(HTTPMethod.post, "blocks")

        result = await self._request(route, json=payload)

        new_data = BlockSchema.transform(result)
        new_block = self._state.create_block(new_data)

        return new_block

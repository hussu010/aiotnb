"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

from attr import dataclass

__all__ = ("Bank",)

import asyncio
import logging
from enum import Enum
from typing import TYPE_CHECKING

from nacl.encoding import HexEncoder
from yarl import URL

from .common import (
    Account,
    BankTransaction,
    Block,
    ConfirmationBlock,
    InvalidBlock,
    PaginatedResponse,
)
from .enums import (
    AccountOrder,
    BankOrder,
    BlockOrder,
    ConfirmationBlockOrder,
    InvalidBlockOrder,
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
    CleanSchema,
    ConfirmationBlockSchema,
    CrawlSchema,
    InvalidBlockSchema,
)
from .utils import message_to_bytes

if TYPE_CHECKING:
    from datetime import datetime
    from typing import Any, Optional, Tuple, Union

    from nacl.signing import VerifyKey

    from .enums import CleanCommand, CrawlCommand
    from .keypair import AnyPubKey, Keypair
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

    async def close_session(self):
        await self._state.close()

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
        ~aiotnb.HTTPException
            The request to list accounts failed.

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

    async def set_account_trust(self, account_number: AnyPubKey, trust: float, node_keypair: Keypair) -> Account:
        """
        Update the trust measure this bank has for a given account. You need this bank's signing key to do this.

        Parameters
        ----------
        account_number: :ref:`AnyPubKey <anypubkey>`
            The account number to edit trust for. Accepts a variety of types.

        trust: :class:`float`
            The new trust value for the account.

        node_keypair: :class:`.Keypair`
            The keypair corresponding to the specific bank.

            .. note::

                This must be the **bank's** public key and the **bank's** private key.

        Raises
        ------
        ~aiotnb.Unauthorized
            The server did not accept the message signature.

        ~aiotnb.HTTPException
            The request to update the account failed.

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
            Determines how many transactions to skip before returning data.

        limit: :class:`int`
            Determines the maximum number of transactions to return.

        ordering: :class:`.AccountOrder`
            Determines in what order the results are returned.

        page_limit: :class:`int`
            Determines how many results to return per page, defaults to 100. You should not have to adjust this.

        filter_sender: Optional[:ref:`AnyPubKey <anypubkey>`]
            An account number. Filters results based on sender account number

        filter_fee: Optional[Union[:class:`NodeType`, :class:`str`]]
            A fee type as a string or ``NodeType``. Filters results based on fee.

        filter_recipient: Optional[:ref:`AnyPubKey <anypubkey>`]
            An account number. Filters results based on recipient account number

        Raises
        ------
        ~aiotnb.HTTPException
            The request to list transactions failed.

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
            Determines how many banks to skip before returning data.

        limit: :class:`int`
            Determines the maximum number of banks to return.

        ordering: :class:`.BankOrder`
            Determines in what order the results are returned.

        page_limit: :class:`int`
            Determines how many results to return per page, max of 100. You should not have to adjust this.

        Raises
        ------
        ~aiotnb.HTTPException
            The request to list banks failed.

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

    async def set_bank_trust(self, node_identifier: AnyPubKey, trust: float, node_keypair: Keypair) -> Bank:
        """
        Update the trust measure this bank has for a given bank. You need this bank's signing key to do this.

        Parameters
        ----------
        node_identifier: :ref:`AnyPubKey <anypubkey>`
            The node identifier (NID) of the bank to edit trust for. Accepts a variety of types.

        trust: :class:`float`
            The new trust value for the bank.

        node_keypair: :class:`.Keypair`
            The keypair corresponding to the specific bank.

            .. note::

                This must be the **bank's** public key and the **bank's** private key.

        Raises
        ------
        ~aiotnb.Unauthorized
            The server did not accept the message signature.

        ~aiotnb.HTTPException
            The request to update the bank failed.

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
            Determines how many blocks to skip before returning data.

        limit: :class:`int`
            Determines the maximum number of blocks to return.

        ordering: :class:`.BlockOrder`
            Determines in what order the results are returned.

        page_limit: :class:`int`
            Determines how many results to return per page, defaults to 100. You should not have to adjust this.

        filter_sender: Optional[:ref:`AnyPubKey <anypubkey>`]
            An account number as a string. Filters results based on sender account number

        Raises
        ------
        ~aiotnb.HTTPException
            The request to list blocks failed.

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

        ~aiotnb.HTTPException
            The request to add a block failed.

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

    async def clean_status(self) -> Tuple[Optional[str], Optional[datetime]]:
        """
        Request information about the last clean this node ran.

        Raises
        ------
        ~aiotnb.HTTPException
            The clean status request failed.

        Returns
        -------
        Tuple[Optional[:class:`str`], Optional[class:`datetime.datetime`]]
            A two-tuple containing the clean status and last clean time, if present. If no clean has been run, this is ``(None, None)``.
        """

        route = Route(HTTPMethod.get, "clean")

        result = await self._request(route)

        good_data = CleanSchema.transform(result)

        return (good_data["clean_status"], good_data["clean_last_completed"])

    async def manage_clean(
        self, command: CleanCommand, node_keypair: Keypair
    ) -> Tuple[Optional[str], Optional[datetime]]:
        """
        Start or stop a clean job on a node. You need the node's signing key to do this.

        Parameters
        ----------
        command: :class:`.CleanCommand`
            An enum value corresponding to the action you wish to run on the node.

        node_keypair: :class:`.Keypair`
            The keypair corresponding to the specific bank.

            .. note::

                This must be the **node's** public key and the **node's** private key.

        Raises
        ------
        ~aiotnb.Unauthorized
            The server did not accept the message signature.

        ~aiotnb.HTTPException
            The request to manage a clean job failed.

        Returns
        -------
        Tuple[Optional[:class:`str`], Optional[class:`datetime.datetime`]]
            A two-tuple containing the clean status and last clean time, if present. If no clean has been run, this is ``(None, None)``.
        """
        payload = {"clean": command.value}

        payload_data = message_to_bytes(payload)
        signed = node_keypair.sign_message(payload_data)

        payload = {
            "message": payload,
            "node_identifier": node_keypair.account_number,
            "signature": signed.signature.decode("utf-8"),
        }

        route = Route(HTTPMethod.post, "clean")

        result = await self._request(route, json=payload)

        good_data = CleanSchema.transform(result)

        return (good_data["clean_status"], good_data["clean_last_completed"])

    async def fetch_config(self) -> Bank:
        """
        Updates this bank object from node config data.

        Raises
        ------
        ~aiotnb.HTTPException
            The config data request failed.

        Returns
        -------
        :class:`.Bank`
            This object with updated information.
        """

        route = Route(HTTPMethod.get, "config")

        data = await self._request((route))

        new_data = BankConfig.transform(data)

        return self._state.create_bank(new_data)

    async def fetch_confirmation_blocks(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        ordering: ConfirmationBlockOrder = ConfirmationBlockOrder.created,
        page_limit: int = 100,
        **kwargs: Any,
    ) -> PaginatedResponse[ConfirmationBlock]:
        """
        Request a list of confirmation blocks a bank is aware of.

        Returns an async iterator over ``ConfirmationBlock`` objects.

        .. seealso::

            For details about the iterator, see :class:`AsyncIterator`.

        Parameters
        ----------
        offset: :class:`int`
            Determines how many blocks to skip before returning data.

        limit: :class:`int`
            Determines the maximum number of blocks to return.

        ordering: :class:`.ConfirmationBlockOrder`
            Determines in what order the results are returned.

        page_limit: :class:`int`
            Determines how many results to return per page, defaults to 100. You should not have to adjust this.

        Raises
        ------
        ~aiotnb.HTTPException
            The request to list confirmation blocks failed.

        Yields
        ------
        :class:`.ConfirmationBlock`
            Block information.
        """
        payload = {"offset": offset, "limit": page_limit, "ordering": ordering.value}

        _, url = Route(HTTPMethod.get, "confirmation_blocks").resolve(self.address)

        paginator = PaginatedResponse(
            self._state, ConfirmationBlockSchema, ConfirmationBlock, url, limit=limit, params=payload
        )

        return paginator

    # TODO: POST /confirmation_blocks

    async def crawl_status(self) -> Tuple[Optional[str], Optional[datetime]]:
        """
        Request information about the last crawl this node ran.

        Raises
        ------
        ~aiotnb.HTTPException
            The crawl status request failed.

        Returns
        -------
        Tuple[Optional[:class:`str`], Optional[class:`datetime.datetime`]]
            A two-tuple containing the crawl status and last crawl time, if present. If no crawl has been run, this is ``(None, None)``.
        """

        route = Route(HTTPMethod.get, "crawl")

        result = await self._request(route)

        good_data = CleanSchema.transform(result)

        return (good_data["crawl_status"], good_data["crawl_last_completed"])

    async def manage_crawl(
        self, command: CrawlCommand, node_keypair: Keypair
    ) -> Tuple[Optional[str], Optional[datetime]]:
        """
        Start or stop a crawl job on a node. You need the node's signing key to do this.

        Parameters
        ----------
        command: :class:`.CrawlCommand`
            An enum value corresponding to the action you wish to run on the node.

        node_keypair: :class:`.Keypair`
            The keypair corresponding to the specific bank.

            .. note::

                This must be the **node's** public key and the **node's** private key.

        Raises
        ------
        ~aiotnb.Unauthorized
            The server did not accept the message signature.

        ~aiotnb.HTTPException
            The request to manage a crawl job failed.

        Returns
        -------
        Tuple[Optional[:class:`str`], Optional[class:`datetime.datetime`]]
            A two-tuple containing the crawl status and last crawl time, if present. If no crawl has been run, this is ``(None, None)``.
        """
        payload = {"crawl": command.value}

        payload_data = message_to_bytes(payload)
        signed = node_keypair.sign_message(payload_data)

        payload = {
            "message": payload,
            "node_identifier": node_keypair.account_number,
            "signature": signed.signature.decode("utf-8"),
        }

        route = Route(HTTPMethod.post, "crawl")

        result = await self._request(route, json=payload)

        good_data = CleanSchema.transform(result)

        return (good_data["crawl_status"], good_data["crawl_last_completed"])

    async def fetch_invalid_blocks(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        ordering: InvalidBlockOrder = InvalidBlockOrder.created,
        page_limit: int = 100,
        **kwargs: Any,
    ) -> PaginatedResponse[InvalidBlock]:
        """
        Request a list of invalid blocks a bank is aware of.

        Returns an async iterator over ``InvalidBlock`` objects.

        .. seealso::

            For details about the iterator, see :class:`AsyncIterator`.

        Parameters
        ----------
        offset: :class:`int`
            Determines how many blocks to skip before returning data.

        limit: :class:`int`
            Determines the maximum number of blocks to return.

        ordering: :class:`.InvalidBlockOrder`
            Determines in what order the results are returned.

        page_limit: :class:`int`
            Determines how many results to return per page, defaults to 100. You should not have to adjust this.

        Raises
        ------
        ~aiotnb.HTTPException
            The request to list invalid blocks failed.

        Yields
        ------
        :class:`.InvalidBlock`
            Block information.
        """
        payload = {"offset": offset, "limit": page_limit, "ordering": ordering.value}

        _, url = Route(HTTPMethod.get, "invalid_blocks").resolve(self.address)

        paginator = PaginatedResponse(self._state, InvalidBlockSchema, InvalidBlock, url, limit=limit, params=payload)

        return paginator

        # TODO: POST /invalid_blocks

    async def connect_to_node(
        self,
        address: Union[URL, str],
        node_keypair: Keypair,
        *,
        port: Optional[int] = None,
        protocol: Optional[Union[UrlProtocol, str]] = None,
    ) -> bool:
        """
        Send a connection request to this bank node.

        .. note::
            The provided keypair should belong to the node at the given address.

        Parameters
        ----------
        address: Union[:class:`~yarl.URL`, :class:`str`]
            The address of the requesting node. If this is a fully-formed URL, the port and protocol will be acquired from it, if not otherwise provided.

        node_keypair: :class:`.Keypair`
            The keypair corresponding to the requesting node.

        port: Optional[:class:`int`]
            TCP port to use for the connection.
            This defaults to the default port for the provided protocol.

        protocol: Optional[Union[:class:`.UrlProtocol`, :class:`str`]]
            The communication protocol to use for the connection.
            If ``address`` is a fully-formed URL, this parameter is not necessary.

        Raises
        ------
        :exc:`ValueError`
            The parameters supplied were an incorrect configuration.

        ~aiotnb.Unauthorized
            The connection request signature was invalid.

        ~aiotnb.HTTPException
            The connection request failed.

        Returns
        -------
        :class:`bool`
            A boolean value indicating the connection request status. ``True`` if the request was accepted.
        """

        node_address = URL(address)

        if not node_address.host:
            raise ValueError(f"Expected a host in URL: {node_address}")

        if protocol is not None:
            if not isinstance(protocol, UrlProtocol):
                try:
                    protocol = UrlProtocol(protocol)

                except:
                    raise ValueError(f"Unknown protocol: {protocol}")

            node_address = node_address.with_scheme(UrlProtocol.value)

        if port is not None:
            # if port is None here, it resets to default for scheme (thanks yarl)
            node_address = node_address.with_port(port)

        message = {"ip_address": node_address.host, "port": node_address.port, "protocol": node_address.scheme}

        data = message_to_bytes(message)
        signed = node_keypair.sign_message(data)

        payload = {
            "message": message,
            "node_identifier": node_keypair.account_number,
            "signature": signed.signature.decode("utf-8"),
        }

        route = Route(HTTPMethod.post, "connection_requests")

        result = await self._request(route, json=payload)

        _log.debug(f"Connection request got {result!r}")

        if result == {}:
            return True

        # TODO: other failure cases here

        return False

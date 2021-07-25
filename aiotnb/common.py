"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = (
    "Account",
    "BankDetails",
    "BankTransaction",
    "Block",
    "ConfirmationBlock",
    "ConfirmationService",
    "InvalidBlock",
    "ValidatorDetails",
    "PaginatedResponse",
)

import asyncio
import logging
from typing import TYPE_CHECKING, TypeVar

from nacl.signing import VerifyKey
from yarl import URL

from . import validation
from .enums import NodeType, UrlProtocol
from .http import HTTPMethod, Route
from .iter import _PaginatedIterator
from .schemas import BankDetailsSchema, ValidatorDetailsSchema

if TYPE_CHECKING:
    from datetime import datetime
    from typing import Any, Mapping, Optional, Type

    from .state import InternalState


_log = logging.getLogger(__name__)

# Common classes


class Account:
    """
    Represents a keypair account on the TNB network.

    Attributes
    ----------
    id: :class:`str`
        A unique identifier representing this account across the network.

    created: :class:`datetime.datetime`
        Date the account was first seen on the network.

    modified: :class:`datetime.datetime`
        Date the account last was modified. This includes balance changes, etc. (TODO)

    account_number: :class:`str`
        This account's unique address. Also its public key.

    trust: :class:`float`
        The trust amount assigned to this account by a given Bank. Can be different across banks.

    bank_id: :class:`str`
        The node identifier (NID) of the bank this account was received from. This is only useful when looking at account trust.
    """

    __slots__ = (
        "id",
        "created",
        "modified",
        "trust",
        "bank_id",
        "account_number",
        "_account_number",
    )

    def __init__(
        self,
        *,
        id: str,
        created_date: datetime,
        modified_date: datetime,
        account_number: VerifyKey,
        trust: float,
        bank_id: str,
    ):
        self.id = id
        self.created = created_date
        self.modified = modified_date
        self.trust = trust
        self.bank_id = bank_id

        self.account_number = bytes(account_number).hex()
        self._account_number = account_number

    def _update(self, *, created_date: datetime, modified_date: datetime, trust: float, **kwargs):
        self.id = id
        self.created = created_date
        self.modified = modified_date
        self.trust = trust

    def __repr__(self):
        return f"<Account({self.account_number})>"


class BankDetails:
    """
    Represents a partially known bank node on the TNB network.

    Attributes
    ----------

    account_number: :class:`str`
        The account this bank uses to receive transaction fees.

    node_identifier: :class:`str`
        The node identifier (NID) of this bank node.

    version: :class:`str`
        The version identifier of this node.

    transaction_fee: :class:`int`
        The fee this node charges for handling transactions.

    ip_address: :class:`str`
        The IP address of this bank node.

    port: Optional[:class:`int`]
        The port number this node accepts connections on.

    protocol: :class:`.UrlProtocol`
        An enum value representing the scheme this node handles connections with.

    trust: :class:`float`
        The trust amount assigned to this bank by a given bank node. Can be different across banks.

    bank_id: :class:`str`
        The node identifier (NID) of the bank this bank was received from. This is only useful when looking at bank trust.
    """

    __slots__ = (
        "account_number",
        "_account_number",
        "node_identifier",
        "_node_identifier",
        "version",
        "transaction_fee",
        "ip_address",
        "port",
        "protocol",
        "trust",
        "bank_id",
        "_state",
    )

    def __init__(
        self,
        _state,
        *,
        account_number: VerifyKey,
        node_identifier: VerifyKey,
        version: str,
        default_transaction_fee: int,
        ip_address: URL,
        port: Optional[int],
        protocol: UrlProtocol,
        trust: float,
        bank_id: VerifyKey,
    ):
        self.account_number = bytes(account_number).hex()
        self._account_number = account_number

        self.node_identifier = bytes(node_identifier).hex()
        self._node_identifier = node_identifier

        self.version = version
        self.transaction_fee = default_transaction_fee
        self.ip_address = str(ip_address)
        self.port = port
        self.protocol = protocol
        self.trust = trust
        self.bank_id = bank_id

        self._state = _state

    async def upgrade(self):
        url_base = URL.build(scheme=self.protocol.value, host=self.ip_address, port=self.port)

        route = Route(HTTPMethod.get, "config").resolve(url_base)

        data = await self._state.client.request(route)

        return self._state.create_bank(BankDetailsSchema.transform(data))

    def __repr__(self):
        return f"<BankDetails(node_identifier={self.node_identifier})>"


class BankTransaction:
    """
    Represents a bank transaction on the TNB network.

    Attributes
    ----------
    id: :class:`str`
        The transaction ID on the network.

    block: :class:`.Block`
        Network Block this transaction is a part of.

    amount: :class:`int`
        Amount of TNBC involved in this transaction.

    fee_paid_to: Optional[:class:`.NodeType`]
        Indicates what node type received this fee payment. If this is ``None``, then the transaction is not a fee payment.

    memo: :class:`str`
        Memo text sent with the transaction.

    recipient: :class:`str`
        Recipient's account number.

    bank_id: :class:`str`
        The node identifier (NID) of the bank this transaction was received from.
    """

    __slots__ = (
        "id",
        "block",
        "amount",
        "fee_paid_to",
        "memo",
        "recipient",
        "_recipient",
        "bank_id",
    )

    def __init__(
        self, *, id: str, block: Block, fee: NodeType, memo: str, amount: int, recipient: VerifyKey, bank_id: str
    ):
        self.id = id
        self.block = block
        self.amount = amount
        self.fee_paid_to = None if fee == NodeType._none else fee
        self.memo = memo

        self.recipient = bytes(recipient).hex()
        self._recipient = recipient

        self.bank_id = bank_id

    def __repr__(self):
        return f"<BankTransaction(id={self.id})>"


class Block:
    """
    Represents a transaction block on the TNB network.

    Attributes
    ----------
    id: :class:`str`
        The block ID on the network.

    created: :class:`datetime.datetime`
        Date when the block was created.

    modified: :class:`datetime.datetime`
        Date when the block was last modified.

    balance_key: :class:`str`
        Balance key for this block.

    sender: :class:`str`
        Sender's account number.

    signature: :class:`str`
        Signature for this block.

    """

    __slots__ = (
        "id",
        "created",
        "modified",
        "balance_key",
        "_balance_key",
        "sender",
        "_sender",
        "signature",
        "_signature",
    )

    def __init__(
        self,
        *,
        id: str,
        created_date: datetime,
        modified_date: datetime,
        balance_key: VerifyKey,
        sender: VerifyKey,
        signature: bytes,
    ):
        self.id = id
        self.created = created_date
        self.modified = modified_date

        self.signature = signature.hex()
        self._signature = signature

        self.balance_key = bytes(balance_key).hex()
        self._balance_key = balance_key

        self.sender = bytes(sender).hex()
        self._sender = sender

    def __repr__(self):
        return f"<Block(id={self.id})>"


class ConfirmationBlock:
    """
    Represents a confirmed block on the TNB blockchain.

    Attributes
    ----------
    id: :class:`str`
        Unique identifier for this block.

    created: :class:`datetime.datetime`
        Date when this block was created.

    modified: :class:`datetime.datetime`
        Date when this block was last modified.

    block_identifier: :class:`str`
        The identifier of the underlying block.

    block: :class:`str`
        A unique identifier referring to the block. (TODO: what is the difference in these??)

    validator: :class:`str`
        ??? Some other identifier for a validator? (TODO: more info)
    """

    __slots__ = (
        "id",
        "created",
        "modified",
        "block",
        "validator",
        "block_identifier",
        "_block_identifier",
    )

    def __init__(
        self,
        *,
        id: str,
        created_date: datetime,
        modified_date: datetime,
        block_identifier: VerifyKey,
        block: str,
        validator: str,
    ):
        self.id = id
        self.created = created_date
        self.modified = modified_date
        self.block = block
        self.validator = validator

        self.block_identifier = bytes(block_identifier).hex()
        self._block_identifier = block_identifier

    def __repr__(self):
        return f"<ConfirmationBlock(id={self.id})>"


class ConfirmationService:
    """
    Represents an agreement for confirmation services for a period of time.

    Attributes
    ----------
    id: :class:`str`
        Unique identifier for this service timespan.

    created: :class:`datetime.datetime`
        Date this service was created.

    modified: :class:`datetime.datetime`
        Date this service was modified.

    end: :class:`datetime.datetime`
        Date this service period ends.

    start: :class:`datetime.datetime`
        Date this service period starts.

    validator: :class:`str`
        Validator ID ?? (TODO: info)
    """

    __slots__ = ("id", "created", "modified", "end", "start", "validator")

    def __init__(
        self,
        *,
        id: str,
        created_date: datetime,
        modified_date: datetime,
        end: datetime,
        start: datetime,
        validator: str,
    ):
        self.id = id
        self.created = created_date
        self.modified = modified_date
        self.end = end
        self.start = start
        self.validator = validator

    def __repr__(self):
        return f"<ConfirmationService(id={self.id})>"


class InvalidBlock:
    """
    Represents a invalid block on the TNB blockchain.

    Attributes
    ----------
    id: :class:`str`
        Unique identifier for this block.

    created: :class:`datetime.datetime`
        Date when this block was created.

    modified: :class:`datetime.datetime`
        Date when this block was last modified.

    block_identifier: :class:`str`
        The identifier of the underlying block.

    block: :class:`str`
        A unique identifier referring to the block. (TODO: what is the difference in these??)

    confirmation_validator: :class:`str`
        CV identifer (TODO: info)

    primary_validator: :class:`str`
        ??? Some other identifier for a PV? (TODO: more info)
    """

    __slots__ = (
        "id",
        "created",
        "modified",
        "block",
        "confirmation_validator",
        "primary_validator",
        "block_identifier",
        "_block_identifier",
    )

    def __init__(
        self,
        *,
        id: str,
        created_date: datetime,
        modified_date: datetime,
        block_identifier: VerifyKey,
        block: str,
        confirmation_validator: str,
        primary_validator: str,
    ):
        self.id = id
        self.created = created_date
        self.modified = modified_date
        self.block = block

        self.confirmation_validator = confirmation_validator
        self.primary_validator = primary_validator

        self.block_identifier = bytes(block_identifier).hex()
        self._block_identifier = block_identifier

    def __repr__(self):
        return f"<InvalidBlock(id={self.id})>"


class ValidatorDetails:
    """
    Represents a partially known validator node on the TNB network.

    Attributes
    ----------

    account_number: :class:`str`
        The account this bank uses to receive transaction fees.

    node_identifier: :class:`str`
        The node identifier (NID) of this bank node.

    version: :class:`str`
        The version identifier of this node.

    transaction_fee: :class:`int`
        The fee this node charges for handling transactions.

    ip_address: :class:`str`
        The IP address of this bank node.

    port: Optional[:class:`int`]
        The port number this node accepts connections on.

    protocol: :class:`.UrlProtocol`
        An enum value representing the scheme this node handles connections with.

    trust: :class:`float`
        The trust amount assigned to this bank by a given bank node. Can be different across banks.

    bank_id: :class:`str`
        The node identifier (NID) of the bank this bank was received from. This is only useful when looking at bank trust.

    root_account_file: :class:`~yarl.URL`
        URL pointing to the root account file (RAF) for this validator.

    root_account_file_hash: :class:`str`
        Hash of this validator's RAF as a hex-encoded string.

    seed_block_identifier: :class:`str`
        ???

    daily_confirmations: :class:`int`
        Number of confirmations per day this validator processes.
    """

    __slots__ = (
        "account_number",
        "_account_number",
        "node_identifier",
        "_node_identifier",
        "version",
        "transaction_fee",
        "ip_address",
        "port",
        "protocol",
        "trust",
        "bank_id",
        "root_account_file",
        "root_account_file_hash",
        "_root_account_file_hash",
        "seed_block_identifier",
        "daily_confirmations",
        "_state",
    )

    def __init__(
        self,
        _state,
        *,
        account_number: VerifyKey,
        node_identifier: VerifyKey,
        version: str,
        default_transaction_fee: int,
        ip_address: URL,
        port: Optional[int],
        protocol: UrlProtocol,
        trust: float,
        bank_id: VerifyKey,
        root_account_file: URL,
        root_account_file_hash: bytes,
        seed_block_identifier: str,
        daily_confirmation_rate: int,
    ):
        self.account_number = bytes(account_number).hex()
        self._account_number = account_number

        self.node_identifier = bytes(node_identifier).hex()
        self._node_identifier = node_identifier

        self.version = version
        self.transaction_fee = default_transaction_fee
        self.ip_address = str(ip_address)
        self.port = port
        self.protocol = protocol
        self.trust = trust
        self.bank_id = bank_id

        self.root_account_file = root_account_file
        self.root_account_file_hash = root_account_file_hash.hex()
        self._root_account_file_hash = root_account_file_hash

        self.seed_block_identifier = seed_block_identifier
        self.daily_confirmations = daily_confirmation_rate

        self._state = _state

    async def upgrade(self):
        # TODO (Validator milestone) Make this use ValidatorConfig

        raise NotImplementedError()

    def __repr__(self):
        return f"<ValidatorDetails(node_identifier={self.node_identifier})>"


T = TypeVar("T")
Url = validation.As(str, URL)

PAGINATOR_BASE = validation.Schema(
    {
        "count": int,
        "next": validation.Maybe(Url),
        "previous": validation.Maybe(Url),
        "results": ...,
    }
)


class PaginatedResponse(_PaginatedIterator[T]):
    """
    An iterator over n-many pages of data from the API. (TODO)

    .. admonition:: Supported Operations

        .. describe:: async for x in y
            Asynchronously iterate over the contents of the iterator.

    """

    def __init__(
        self,
        state: InternalState,
        schema: validation.Schema,
        type_: Type[T],
        url: URL,
        *,
        limit: Optional[int] = None,
        **kwargs: Any,
    ):
        _converter = state.get_creator(type_)

        if _converter is None:
            raise TypeError(f"type {type_} has no creator method in InternalState")
        else:
            self._converter = _converter

        self._state = state
        self._params = kwargs.pop("params", {})
        self._per_page_limit = self._params.get("limit", 100)
        self._url = url.with_query(self._params)

        self._extra_args = kwargs.pop("extra", {})

        self._type = type_
        self._schema = schema
        self._validator = PAGINATOR_BASE.resolve()

        self.limit = limit
        self.received = 0

        self._page = asyncio.Queue()

    async def _next_page(self):
        if self.limit is None or self.limit > self._per_page_limit:
            pull_limit = self._per_page_limit
        else:
            pull_limit = self.limit

        if pull_limit > 0:
            response = await self._state.client.request(("GET", self._url))
            data = self._validator.transform(response)

            if data["next"] is not None:
                self._url = data["next"]
                self._params = dict(self._url.query)
            else:
                self.limit = 0

            item_count = len(data["results"])
            if item_count < self._per_page_limit:
                self.limit = 0

            elif self.limit is not None:
                self.limit -= item_count

            for raw_data in data["results"]:
                parsed_data = self._schema.transform(raw_data)
                await self._page.put(self._converter({**parsed_data, **self._extra_args}))

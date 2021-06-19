"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("Account", "Block", "BankTransaction", "PaginatedResponse")

import asyncio
import logging
from typing import TYPE_CHECKING, TypeVar

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from yarl import URL

from . import validation
from .enums import NodeType
from .iter import _PaginatedIterator

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

    account_number_bytes: :class:`bytes`
        This account's number as hex-encoded bytes.

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
        "account_number_bytes",
        "account_number",
        "_public_key",
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

        self.account_number_bytes = account_number.encode(encoder=HexEncoder)
        self.account_number = self.account_number_bytes.decode("utf-8")
        self._public_key = account_number

    def _update(self, *, created_date: datetime, modified_date: datetime, trust: float, **kwargs):
        self.id = id
        self.created = created_date
        self.modified = modified_date
        self.trust = trust

    def __repr__(self):
        return f"<Account({self.account_number})>"


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

    balance_key_bytes: :class:`bytes`
        Balance key for this block as hex-encoded bytes.

    sender: :class:`str`
        Sender's account number.

    sender_bytes: :class:`bytes`
        The sender's account number as hex-encoded bytes.

    signature: :class:`str`
        Signature for this block.

    signature_bytes: :class:`bytes`
        Signature for this block as hex-encoded bytes.
    """

    __slots__ = (
        "id",
        "created",
        "modified",
        "balance_key",
        "balance_key_bytes",
        "sender",
        "sender_bytes",
        "signature",
        "signature_bytes",
        "_balance_key",
        "_sender_key",
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

        self.signature_bytes = signature
        self.signature = self.signature_bytes.decode("utf-8")

        self.balance_key_bytes = balance_key.encode(encoder=HexEncoder)
        self.balance_key = self.balance_key_bytes.decode("utf-8")

        self.sender_bytes = sender.encode(encoder=HexEncoder)
        self.sender = self.sender_bytes.decode("utf-8")

        self._balance_key = balance_key
        self._sender_key = sender

    def __repr__(self):
        return f"<Block(id={self.id})>"


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

    recipient_bytes: :class:`bytes`
        Recipient's account number as hex-encoded bytes.

    bank_id: :class:`str`
        The node identifier (NID) of the bank this transaction was received from.
    """

    __slots__ = (
        "id",
        "block",
        "amount",
        "fee_paid_to",
        "memo",
        "recipient_bytes",
        "recipient",
        "_recipient_key",
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

        self.recipient_bytes = recipient.encode(encoder=HexEncoder)
        self.recipient = self.recipient_bytes.decode("utf-8")

        self._recipient_key = recipient

        self.bank_id = bank_id

    def __repr__(self):
        return f"<BankTransaction(id={self.id})>"


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

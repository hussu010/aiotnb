"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ()

import inspect
import logging
from typing import TYPE_CHECKING, Any, Callable, Mapping, Type, TypeVar

from nacl.encoding import HexEncoder

from .bank import Bank
from .common import Account, BankTransaction, Block
from .validator import Validator

if TYPE_CHECKING:
    from typing import Optional

    from aiotnb.http import HTTPClient

_log = logging.getLogger(__name__)

T = TypeVar("T", bound=Type)
CreatorFn = Callable[[Mapping[str, Any]], T]


class InternalState:
    def __init__(self, client: HTTPClient):
        self.client = client

        self._nodes = {}
        self._accounts = {}
        self._blockchain = {}
        self._transactions = {}

        creators = {}

        for (name, item) in inspect.getmembers(self):
            if name[:7] == "create_":
                creators[name[7:]] = item

        self._creators = creators

    async def close(self):
        await self.client.close()

    def get_creator(self, type_: T) -> Optional[CreatorFn[T]]:
        type_name = type_.__name__.lower()

        if type_name in self._creators:
            return self._creators[type_name]

    # Creator methods

    # TODO IMPORTANT: handle updating of data while still returning cached object

    def create_bank(self, data) -> Bank:
        node_id = data["node_identifier"].encode(encoder=HexEncoder)

        if node_id in self._nodes:
            return self._nodes[node_id]

        else:
            validator = self.create_validator(data["primary_validator"])
            data["primary_validator"] = validator

            bank = Bank(self, **data)
            self._nodes[bank.node_identifier_bytes] = bank

            return bank

    def create_validator(self, data) -> Validator:
        node_id = data["node_identifier"].encode(encoder=HexEncoder)

        if node_id in self._nodes:
            return self._nodes[node_id]

        else:
            validator = Validator(self, **data)
            self._nodes[validator.node_identifier_bytes] = validator

            return validator

    def create_account(self, data) -> Account:
        account_key = data["id"], data["bank_id"]

        if account_key in self._accounts:
            return self._accounts[account_key]

        else:
            account = Account(**data)
            self._accounts[account.id, account.bank_id] = account

            return account

    def create_banktransaction(self, data) -> BankTransaction:
        tx_key = data["id"], data["bank_id"]

        if tx_key in self._transactions:
            return self._transactions[tx_key]

        else:
            block = self.create_block(**data["block"])
            data["block"] = block

            tx = BankTransaction(**data)
            self._transactions[tx.id, tx.bank_id] = tx

            return tx

    def create_block(self, data) -> Block:
        block_id = data["id"]

        if block_id in self._blockchain:
            return self._blockchain[block_id]

        else:
            block = Block(**data)
            self._blockchain[block.id] = block

            return block

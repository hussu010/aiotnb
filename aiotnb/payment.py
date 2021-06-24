"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

from nacl.signing import VerifyKey

__all__ = ("Payment", "FeePayment", "TransactionBlock")

import logging
from typing import TYPE_CHECKING

from .keypair import key_as_str
from .utils import message_to_bytes

if TYPE_CHECKING:
    from typing import List, Union

    from .bank import Bank
    from .keypair import AnyPubKey, Keypair
    from .validator import Validator

_log = logging.getLogger(__name__)


class _PaymentTransaction:
    amount: int
    recipient: str

    def _to_dict(self):
        raise NotImplemented


class Payment(_PaymentTransaction):
    def __init__(self, amount: int, recipient: AnyPubKey, *, memo: str = ""):
        self.amount = amount
        self.recipient = key_as_str(recipient)
        self.memo = memo

    def _to_dict(self):
        return {"amount": self.amount, "recipient": self.recipient, "memo": self.memo}


class FeePayment(_PaymentTransaction):
    def __init__(self, recipient: Union[Bank, Validator]):
        self.amount = recipient.transaction_fee
        self.recipient = recipient.account_number
        self.fee = recipient.node_type.value

    def _to_dict(self):
        return {"amount": self.amount, "recipient": self.recipient, "fee": self.fee}


class TransactionBlock:
    def __init__(self, keypair: Keypair, balance_key: VerifyKey):
        self.keypair = keypair

        self.balance_key = key_as_str(balance_key)
        self._balance_key = balance_key

        self.txs: List[_PaymentTransaction] = []

    def add_transaction(self, tx: _PaymentTransaction):
        self.txs.append(tx)

    def finalize(self):
        message = {"balance_key": self.balance_key, "txs": [tx._to_dict() for tx in self.txs]}

        signed = self.keypair.sign_message(message_to_bytes(message))

        return {
            "account_number": self.keypair.account_number,
            "message": message,
            "signature": signed.signature.decode("utf-8"),
        }

"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("BankConfig",)

from schema import And, Optional, Or, Schema, Use

from ..models import Bank, ConfirmationValidator, NodeType, UrlProtocol, Validator
from .utils import (
    AccountNumber,
    BalanceLock,
    ISO8601UTCTimestamp,
    OptionalVal,
    Signature,
    Url,
    partial,
)

BankConfig = Schema(
    {
        "primary_validator": dict,
        "account_number": AccountNumber,
        "ip_address": Url,
        "node_identifier": AccountNumber,
        "port": OptionalVal(int),
        "protocol": And(str, Use(UrlProtocol)),
        "version": str,
        "default_transaction_fee": int,
        "node_type": And(str, Use(NodeType)),
    }
)

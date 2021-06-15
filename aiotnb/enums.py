"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("AccountOrder", "TransactionOrder", "UrlProtocol", "NodeType")

import logging
from enum import Enum

_log = logging.getLogger(__name__)

# Ordering enums


class AccountOrder(Enum):
    created = "created_date"
    created_desc = "-created_date"
    modified = "modified_date"
    modified_desc = "-modified_date"
    id = "id"
    id_desc = "-id"
    number = "account_number"
    number_desc = "-account_number"
    trust = "trust"
    trust_desc = "-trust"


class TransactionOrder(Enum):
    amount = "amount"
    amount_desc = "-amount"
    block_created = "block__created_date"
    block_created_desc = "-block__created_date"
    block_modified = "block__modified_date"
    block_modified_desc = "-block__modified_date"
    block_id = "block__id"
    block_id_desc = "-block__id"
    block_sender = "block__sender"
    block_sender_desc = "-block__sender"
    id = "id"
    id_desc = "-id"
    recipient = "recipient"
    recipient_desc = "-recipient"


class UrlProtocol(Enum):
    """
    Specifies a URL scheme to use for a connection.
    """

    http = "http"
    https = "https"


class NodeType(Enum):
    """
    Differentiates between different types of node.
    """

    bank = "BANK"
    primary_validator = "PRIMARY_VALIDATOR"
    confirmation_validator = "CONFIRMATION_VALIDATOR"
    none = ""
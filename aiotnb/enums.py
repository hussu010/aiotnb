"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("AccountOrder", "UrlProtocol", "NodeType")

import logging
from enum import Enum

_log = logging.getLogger(__name__)

# Common classes


class AccountOrder(Enum):
    created_asc = "created_date"
    created_desc = "-created_date"
    modified_asc = "modified_date"
    modified_desc = "-modified_date"
    id_asc = "id"
    id_desc = "-id"
    number_asc = "account_number"
    number_desc = "-account_number"
    trust_asc = "trust"
    trust_desc = "-trust"


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

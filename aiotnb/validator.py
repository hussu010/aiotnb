"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("Validator",)

import logging
from typing import TYPE_CHECKING

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from yarl import URL

from .common import Account, PaginatedResponse
from .enums import AccountOrder, NodeType, UrlProtocol
from .http import HTTPClient, HTTPMethod, Route
from .schemas import AccountSchema, BankConfig
from .validation import transform

if TYPE_CHECKING:
    from typing import Any, List, Mapping, Optional


_log = logging.getLogger(__name__)


class Validator:
    """
    Object representing a Validator on the TNB network.

    """

    pass

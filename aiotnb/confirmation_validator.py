"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("ConfirmationValidator",)

import logging
from typing import TYPE_CHECKING

from nacl.encoding import HexEncoder

from .enums import NodeType
from .errors import ValidatorFailed
from .http import HTTPMethod, Route

if TYPE_CHECKING:
    from typing import Any, Optional

    from nacl.signing import VerifyKey
    from yarl import URL

    from .state import InternalState


_log = logging.getLogger(__name__)


class ConfirmationValidator:
    """
    Object representing a Confirmation Validator on the TNB network.

    """

    pass

    def _update(self, **kwargs):
        pass

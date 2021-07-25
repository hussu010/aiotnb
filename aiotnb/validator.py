"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("Validator",)

import logging
from typing import TYPE_CHECKING

from .enums import NodeType
from .errors import ValidatorFailed
from .http import HTTPMethod, Route

if TYPE_CHECKING:
    from typing import Any, Optional

    from nacl.signing import VerifyKey
    from yarl import URL

    from .state import InternalState


_log = logging.getLogger(__name__)


class Validator:
    """
    Object representing a Validator on the TNB network.

    """

    transaction_fee: int
    account_number: str
    node_type: NodeType

    def __init__(self, state: InternalState, *, node_identifier: VerifyKey, **kwargs):
        self._state = state

        # TODO
        self.node_identifier = bytes(node_identifier).hex()
        self._node_identifier = node_identifier

    def _update(self, **kwargs):
        pass

    async def close_session(self):
        await self._state.close()

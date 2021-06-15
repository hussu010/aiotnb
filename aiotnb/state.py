"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ()

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiotnb.http import HTTPClient

_log = logging.getLogger(__name__)


class InternalState:
    def __init__(self, client: HTTPClient):
        self.client = client

        self._nodes = {}
        self._accounts = {}

    async def close(self):
        await self.client.close()

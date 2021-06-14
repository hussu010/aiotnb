"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ()

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Mapping

try:
    import ujson as json

    _USING_FAST_JSON = True
except ImportError:
    _USING_FAST_JSON = False
    import json


_log = logging.getLogger(__name__)


if not _USING_FAST_JSON:
    _log.warn("ujson not installed, defaulting to json")


# This should be 100% identical to the existing signing method
def message_to_bytes(data: Mapping[str, Any]) -> bytes:
    kwargs: dict[str, Any] = dict(sort_keys=True)

    if not _USING_FAST_JSON:
        kwargs["separators"] = (",", ":")

    return json.dumps(data, **kwargs).encode("utf-8")  # type: ignore

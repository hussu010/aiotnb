"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("Route", "HTTPMethod", "HTTPClient")

import asyncio
import logging
import sys
from enum import Enum
from typing import TYPE_CHECKING, cast
from urllib.parse import quote as _quote

from aiohttp import ClientSession
from yarl import URL

from .errors import Forbidden, HTTPException, NetworkServerError, NotFound

try:
    import ujson as json

    _USING_FAST_JSON = True
except ImportError:
    _USING_FAST_JSON = False
    import json


if TYPE_CHECKING:
    from typing import Any, Mapping, Optional, Tuple, Union
    from asyncio import AbstractEventLoop

    from aiohttp import BasicAuth
    from aiohttp.connector import BaseConnector
    from aiohttp.client_reqrep import ClientResponse

from . import __version__

_log = logging.getLogger(__name__)


if not _USING_FAST_JSON:
    _log.warn("ujson not installed, defaulting to json")


class HTTPMethod(Enum):
    get = "GET"
    post = "POST"
    put = "PUT"
    patch = "PATCH"
    delete = "DELETE"


class Route:
    def __init__(self, method: HTTPMethod, path: str, **params: Any):
        self.method = method

        if params is not None:
            self.path = path.format_map({k: _quote(v) if isinstance(v, str) else v for k, v in params.items()})

        else:
            self.path = path

    def resolve(self, url_base: URL) -> Tuple[str, URL]:
        return (self.method.value, url_base / self.path)


class HTTPClient:
    """
    Represents an HTTP client sending requests to the TNB network.
    """

    def __init__(
        self,
        connector: Optional[BaseConnector] = None,
        *,
        proxy: Optional[str] = None,
        proxy_auth: Optional[BasicAuth] = None,
        loop: Optional[AbstractEventLoop] = None,
    ):
        self.connector = connector
        self.proxy = proxy
        self.proxy_auth = proxy_auth

        self.loop = loop or asyncio.get_event_loop()

        self.__session: Optional[ClientSession] = None

        self.user_agent = f"aiotnb (https://github.com/AnonymousDapper/aiotnb {__version__}) Python/{sys.version_info.major}.{sys.version_info.minor}"

        self._req_count = 0

    @property
    def _session(self) -> Optional[ClientSession]:
        return self.__session

    @staticmethod
    async def parse_data(response: ClientResponse) -> Union[str, Mapping[str, Any]]:
        text = await response.text(encoding="utf-8")

        if response.headers.get("Content-Type") == "application/json":
            try:
                return json.loads(text)

            except:
                pass

        return text

    async def init_session(self):
        if not self.__session:
            self.__session = ClientSession(connector=self.connector, json_serialize=json.dumps)

        else:
            _log.warn("init_session called with existing session")

    async def close(self):
        if self.__session:
            await self.__session.close()

    async def request(self, route_data: Tuple[str, URL], **kwargs: Any) -> Mapping[str, Any]:
        self._req_count += 1

        headers = {"User-Agent": self.user_agent}
        method, url = route_data

        if "json" in kwargs:
            headers["Content-Type"] = "application/json"

        if self.proxy:
            kwargs["proxy"] = self.proxy

        if self.proxy_auth:
            kwargs["proxy_auth"] = self.proxy_auth

        if TYPE_CHECKING:
            self.__session = cast(ClientSession, self.__session)

        async with self.__session.request(method, url, **kwargs) as response:
            _log.debug(f"{method} '{url}' returned {response.status}")

            data = await self.parse_data(response)

            # TODO: this is True is response.status < 400, which may not be appropriate
            if response.ok:
                if TYPE_CHECKING:
                    data = cast(Mapping[str, Any], data)

                return data

            else:
                if TYPE_CHECKING:
                    data = cast(str, data)  # Python typing is such a mess

                _log.error(f"^ {method} failed ({response.reason})")

                if response.status == 403:
                    raise Forbidden(response, data)

                elif response.status == 404:
                    raise NotFound(response, data)

                elif response.status == 503:
                    raise NetworkServerError(response, data)

        raise HTTPException(response, data)

"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("connect_to_bank", "connect_to_pv", "connect_to_cv")

from .http_client import HTTPClient, HTTPMethod, Route
from .models import Bank, ConfirmationValidator, PrimaryValidator


async def connect_to_bank(bank_address: str, *, use_https: bool = False, **kwargs) -> Bank:
    """
    Initiates a connection to a bank in the TNB network and downloads its config data.
    The data is then parsed into an object to easily allow further requests.

    Parameters
    ----------
    bank_address: :class:`str`
        The IP address or hostname of the bank to connect to.

    use_https: Optional[:class:`bool`]
        Whether to enable HTTPS. Defaults to ``False``.

    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The :class:`asyncio.AbstractEventLoop` to use for the underlying HTTP client.
        Defaults to ``None`` and the current event loop is used if omitted.

    connector: Optional[:class:`aiohttp.BaseConnector`]
        The connector to use for connection transport.

    proxy: Optional[:class:`str`]
        Proxy URL, if a proxy is required.

    proxy_auth: Optional[:class:`aiohttp.BasicAuth`]
        Object representing HTTP Basic Authentication for the proxy. Useless without ``proxy`` set.


    Raises
    ------
    :exc:`.Forbidden`
        The bank refused our config request.
        This should not happen.

    :exc:`.NotFound`
        The config URL is not valid.
        This should not happen.

    :exc:`.NetworkServerError`
        The bank encountered an error while attempting to give us the config.

    :exc:`.HTTPException`
        The bank encountered an unknown error.


    Returns
    -------
    :class:`.Bank`
        An object representing the bank at the specified address.
    """

    url_base = f"http{'s' if use_https else ''}://{bank_address}"

    connector = kwargs.get("connector")
    proxy = kwargs.get("proxy")
    proxy_auth = kwargs.get("proxy_auth")
    loop = kwargs.get("loop")

    client = HTTPClient(connector, proxy=proxy, proxy_auth=proxy_auth, loop=loop)

    await client._init_session()

    route = Route(HTTPMethod.Get, "/config").resolve(url_base)

    data = await client.request(route)

    return Bank(data["node_identifier"])


async def connect_to_pv():
    pass


async def connect_to_cv():
    pass

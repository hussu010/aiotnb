"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("connect_to_bank", "connect_to_validator", "connect_to_cv")

import logging
from typing import TYPE_CHECKING

from yarl import URL

from .bank import Bank
from .confirmation_validator import ConfirmationValidator
from .http import HTTPClient, HTTPMethod, Route
from .schemas import BankConfig
from .state import InternalState
from .validation import transform
from .validator import Validator

if TYPE_CHECKING:
    from typing import Any

_log = logging.getLogger(__name__)


async def connect_to_bank(bank_address: str, *, port: int = 80, use_https: bool = False, **kwargs: Any) -> Bank:
    """
    Initiates a connection to a bank in the TNB network and downloads its config data.

    The data is then parsed into an object to easily allow further requests.

    Parameters
    ----------
    bank_address: :class:`str`
        The IP address or hostname of the bank to connect to.

    port: :class:`int`
        The port to use to connect to the bank. Defaults to 80.

    use_https: Optional[:class:`bool`]
        Whether to enable HTTPS. Defaults to ``False``.

    loop: Optional[:class:`~asyncio.AbstractEventLoop`]
        The event loop to use for the underlying HTTP client.
        Defaults to ``None`` and the current event loop is used if omitted.

    connector: Optional[:class:`~aiohttp.BaseConnector`]
        The connector to use for connection transport.

    proxy: Optional[:class:`str`]
        Proxy URL, if a proxy is required.

    proxy_auth: Optional[:class:`~aiohttp.BasicAuth`]
        Object representing HTTP Basic Authentication for the proxy. Useless without ``proxy`` set.

    Raises
    ------
    :exc:`Forbidden`
        The bank refused our config request.
        This should not happen.

    :exc:`NotFound`
        The config URL is not valid.
        This should not happen.

    :exc:`NetworkServerError`
        The bank encountered an error while attempting to give us the config.

    :exc:`HTTPException`
        The bank encountered an unknown error.

    Returns
    -------
    :class:`Bank`
        An object representing the bank at the specified address.
    """

    # url_base = f"http{'s' if use_https else ''}://{bank_address}"
    url_base = URL.build(scheme="https" if use_https else "http", host=bank_address, port=port)

    connector = kwargs.get("connector")
    proxy = kwargs.get("proxy")
    proxy_auth = kwargs.get("proxy_auth")
    loop = kwargs.get("loop")

    client = HTTPClient(connector, proxy=proxy, proxy_auth=proxy_auth, loop=loop)

    state = InternalState(client)

    await client.init_session()

    route = Route(HTTPMethod.get, "config").resolve(url_base)

    data = await client.request(route)

    new_data = transform(BankConfig, data)

    return Bank(state, **new_data)


async def connect_to_cv(
    cv_address: str, *, port: int = 80, use_https: bool = False, **kwargs: Any
) -> ConfirmationValidator:
    """
    Initiates a connection to a confirmation validator in the TNB network and downloads its config data.

    The data is then parsed into an object to easily allow further requests.

    Parameters
    ----------
    cv_address: :class:`str`
        The IP address or hostname of the CV to connect to.

    port: :class:`int`
        The port to use to connect to the CV. Defaults to 80.

    use_https: Optional[:class:`bool`]
        Whether to enable HTTPS. Defaults to ``False``.

    loop: Optional[:class:`~asyncio.AbstractEventLoop`]
        The event loop to use for the underlying HTTP client.
        Defaults to ``None`` and the current event loop is used if omitted.

    connector: Optional[:class:`~aiohttp.BaseConnector`]
        The connector to use for connection transport.

    proxy: Optional[:class:`str`]
        Proxy URL, if a proxy is required.

    proxy_auth: Optional[:class:`~aiohttp.BasicAuth`]
        Object representing HTTP Basic Authentication for the proxy. Useless without ``proxy`` set.

    Raises
    ------
    :exc:`Forbidden`
        The CV refused our config request.
        This should not happen.

    :exc:`NotFound`
        The config URL is not valid.
        This should not happen.

    :exc:`NetworkServerError`
        The CV encountered an error while attempting to give us the config.

    :exc:`HTTPException`
        The CV encountered an unknown error.

    Returns
    -------
    :class:`ConfirmationValidator`
        An object representing the CV at the specified address.
    """

    # url_base = f"http{'s' if use_https else ''}://{cv_address}"
    url_base = URL.build(scheme="https" if use_https else "http", host=cv_address, port=port)

    connector = kwargs.get("connector")
    proxy = kwargs.get("proxy")
    proxy_auth = kwargs.get("proxy_auth")
    loop = kwargs.get("loop")

    client = HTTPClient(connector, proxy=proxy, proxy_auth=proxy_auth, loop=loop)

    await client.init_session()

    route = Route(HTTPMethod.get, "config").resolve(url_base)

    data = await client.request(route)

    return ConfirmationValidator()


async def connect_to_validator(
    validator_address: str, *, port: int = 80, use_https: bool = False, **kwargs: Any
) -> Validator:
    """
    Initiates a connection to a validator in the TNB network and downloads its config data.

    The data is then parsed into an object to easily allow further requests.

    Parameters
    ----------
    validator_address: :class:`str`
        The IP address or hostname of the validator to connect to.

    port: :class:`int`
        The port to use to connect to the validator. Defaults to 80.

    use_https: Optional[:class:`bool`]
        Whether to enable HTTPS. Defaults to ``False``.

    loop: Optional[:class:`~asyncio.AbstractEventLoop`]
        The event loop to use for the underlying HTTP client.
        Defaults to ``None`` and the current event loop is used if omitted.

    connector: Optional[:class:`~aiohttp.BaseConnector`]
        The connector to use for connection transport.

    proxy: Optional[:class:`str`]
        Proxy URL, if a proxy is required.

    proxy_auth: Optional[:class:`~aiohttp.BasicAuth`]
        Object representing HTTP Basic Authentication for the proxy. Useless without ``proxy`` set.


    Raises
    ------
    :exc:`Forbidden`
        The validator refused our config request.
        This should not happen.

    :exc:`NotFound`
        The config URL is not valid.
        This should not happen.

    :exc:`NetworkServerError`
        The validator encountered an error while attempting to give us the config.

    :exc:`HTTPException`
        The validator encountered an unknown error.


    Returns
    -------
    :class:`Validator`
        An object representing the validator at the specified address.
    """

    # url_base = f"http{'s' if use_https else ''}://{validator_address}"
    url_base = URL.build(scheme="https" if use_https else "http", host=validator_address, port=port)

    connector = kwargs.get("connector")
    proxy = kwargs.get("proxy")
    proxy_auth = kwargs.get("proxy_auth")
    loop = kwargs.get("loop")

    client = HTTPClient(connector, proxy=proxy, proxy_auth=proxy_auth, loop=loop)

    await client.init_session()

    route = Route(HTTPMethod.get, "config").resolve(url_base)

    data = await client.request(route)

    return Validator()

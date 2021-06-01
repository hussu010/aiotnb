"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

from typing import Any, Union

__all__ = ("connect_to_bank", "connect_to_pv", "connect_to_cv", "LocalAccount")

import logging
from pathlib import Path

from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from nacl.exceptions import ValueError as NACLValueError
from nacl.signing import SignedMessage, SigningKey, VerifyKey

from .exceptions import (
    KeyfileNotFound,
    KeysignException,
    SignatureVerifyFailed,
    SigningKeyLoadFailed,
    VerifyKeyLoadFailed,
)
from .http import HTTPClient, HTTPMethod, Route
from .models import Bank, ConfirmationValidator, PrimaryValidator

log = logging.getLogger(__name__)


async def connect_to_bank(bank_address: str, *, use_https: bool = False, **kwargs: Any) -> Bank:
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

    url_base = f"http{'s' if use_https else ''}://{bank_address}"

    connector = kwargs.get("connector")
    proxy = kwargs.get("proxy")
    proxy_auth = kwargs.get("proxy_auth")
    loop = kwargs.get("loop")

    client = HTTPClient(connector, proxy=proxy, proxy_auth=proxy_auth, loop=loop)

    await client.init_session()

    route = Route(HTTPMethod.Get, "/config").resolve(url_base)

    data = await client.request(route)

    return Bank()


async def connect_to_cv(cv_address: str, *, use_https: bool = False, **kwargs: Any) -> ConfirmationValidator:
    """
    Initiates a connection to a confirmation validator in the TNB network and downloads its config data.

    The data is then parsed into an object to easily allow further requests.

    Parameters
    ----------
    bank_address: :class:`str`
        The IP address or hostname of the CV to connect to.

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

    url_base = f"http{'s' if use_https else ''}://{cv_address}"

    connector = kwargs.get("connector")
    proxy = kwargs.get("proxy")
    proxy_auth = kwargs.get("proxy_auth")
    loop = kwargs.get("loop")

    client = HTTPClient(connector, proxy=proxy, proxy_auth=proxy_auth, loop=loop)

    await client.init_session()

    route = Route(HTTPMethod.Get, "/config").resolve(url_base)

    data = await client.request(route)

    return ConfirmationValidator()


async def connect_to_pv(pv_address: str, *, use_https: bool = False, **kwargs: Any) -> PrimaryValidator:
    """
    Initiates a connection to a primary validator in the TNB network and downloads its config data.

    The data is then parsed into an object to easily allow further requests.

    Parameters
    ----------
    pv_address: :class:`str`
        The IP address or hostname of the PV to connect to.

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
    :exc:`Forbidden`
        The PV refused our config request.
        This should not happen.

    :exc:`NotFound`
        The config URL is not valid.
        This should not happen.

    :exc:`NetworkServerError`
        The PV encountered an error while attempting to give us the config.

    :exc:`HTTPException`
        The PV encountered an unknown error.


    Returns
    -------
    :class:`PrimaryValidator`
        An object representing the PV at the specified address.
    """

    url_base = f"http{'s' if use_https else ''}://{pv_address}"

    connector = kwargs.get("connector")
    proxy = kwargs.get("proxy")
    proxy_auth = kwargs.get("proxy_auth")
    loop = kwargs.get("loop")

    client = HTTPClient(connector, proxy=proxy, proxy_auth=proxy_auth, loop=loop)

    await client.init_session()

    route = Route(HTTPMethod.Get, "/config").resolve(url_base)

    data = await client.request(route)

    return PrimaryValidator()


class LocalAccount:
    """
    Represents a local keypair account.

    .. container:: operations

        .. describe:: x == y
            Checks if the keypairs for both accounts are equal.

    Attributes
    ----------
    account_number: :class:`bytes`
        The network account number as hex-encoded bytes.
        The account number is the public key.

    signing_key:  :class:`bytes`
        The signing key for the account as hex-encoded bytes.
        The signing key is the **private** key.

        .. warning:: Do not share this key. This is the private key and can be used to impersonate you.
    """

    def __init__(self, private_key: SigningKey):
        """
        Create a new local account object from an existing private key.

        Parameters
        ----------
        sign_key: :class:`nacl.signing.SigningKey`
            The private key for the keypair. The verify key will be derived from the private key.
        """

        self._sign_key = private_key
        self._verify_key = private_key.verify_key

        self.signing_key = private_key.encode(encoder=HexEncoder)
        self.account_number = self._verify_key.encode(encoder=HexEncoder)

    @classmethod
    def from_key_file(cls, key_file: Union[Path, str]) -> LocalAccount:
        """
        Load an account from an existing private key file.

        Parameters
        ----------
        key_file: Union[:class:`pathlib.Path`, :class:`str`]
            The file path to load a keyfile from.

        Raises
        ------
        :exc:`KeyfileNotFound`
            The specified file was not found.

        :exc:`SigningKeyLoadFailed`
            The private key contained in the keyfile was not a proper key.

        :exc:`KeysignException`
            The keyfile was present but could not be read.
        """
        file_path = Path(key_file).resolve() if not isinstance(key_file, Path) else key_file.resolve()
        raw_key: bytes

        if file_path.exists() and file_path.is_file():
            try:
                raw_key = file_path.read_bytes()

            except Exception as e:
                log.error("keyfile could not be read")
                raise KeysignException("keyfile could not be read", original=e) from e

        else:
            log.error("keyfile path was not found")
            raise KeyfileNotFound(f"'{file_path.name}' was not found on the system")

        signing_key: SigningKey

        try:
            signing_key = SigningKey(raw_key, encoder=HexEncoder)

        except Exception as e:
            log.error("private key load failed")
            raise SigningKeyLoadFailed("key must be 32 bytes long and hex-encoded", original=e) from e

        return cls(signing_key)

    @classmethod
    def generate(cls) -> LocalAccount:
        """
        Generates a new keypair and load an account from it.
        """

        return cls(SigningKey.generate())

    def write_key_file(self, key_file: Union[Path, str]):
        """
        Write out the account's private key for safekeeping.

        Parameters
        ----------
        key_file_path: Union[:class:`pathlib.Path`, :class:`str`]
            The file path to save the key to.

        Raises
        ------
        :exc:`KeyfileNotFound`
            The specified file path already exists.
            This method will *not* overwrite existing files.

        :exc:`KeysignException`
            The keyfile could not be written to.
        """

        file_path = Path(key_file).resolve() if not isinstance(key_file, Path) else key_file.resolve()

        if not file_path.exists():
            try:
                file_path.write_bytes(self.signing_key)

            except Exception as e:
                log.error("keyfile write failed")
                raise KeysignException("keyfile could not be written", original=e) from e

        else:
            log.error("keyfile already exists, not overwriting.")
            raise KeyfileNotFound(f"'{file_path.name}' already exists")

    def sign_message(self, message: bytes) -> SignedMessage:
        """
        Signs a given message and returns the signature as hex-encoded bytes.

        Parameters
        ----------
        message: :class:`bytes`
            The message data to sign.

        Returns
        -------
        :class:`nacl.signing.SignedMessage`
            The signature data.

        """

        return self._sign_key.sign(message, encoder=HexEncoder)

    @staticmethod
    def verify(signed_message: SignedMessage, verify_key: VerifyKey) -> bytes:
        """
        Takes a signed message, a signature, and a public key, and attempts to verify the signature on the message.

        Parameters
        ----------
        message: :class:`nacl.signing.SignedMessage`
            The signed message + signature data.

        verify_key: :class:`nacl.signing.VerifyKey`
            The sender's public key data.

        Raises
        ------

        :exc:`SignatureVerifyFailed`
            The signature did not match the public key.

        Returns
        -------
        :class:`bytes`
            The verified message data
        """
        try:
            verified_message = verify_key.verify(signed_message, encoder=HexEncoder)

        except BadSignatureError as e:
            log.error("verify: signature failed")
            raise SignatureVerifyFailed("verify signature bad", original=e) from e

        return verified_message

    @staticmethod
    def verify_raw(message: bytes, signature: bytes, verify_key: bytes) -> bytes:
        """
        Takes a signed message, a signature, and a public key, and attempts to verify the signature on the message.

        Parameters
        ----------
        message: :class:`bytes`
            The signed message data to validate.

        signature: :class:`bytes`
            The signature data attached to the message.

        verify_key: :class:`bytes`
            The sender's public key data.

        Raises
        ------
        :exc:`VerifyKeyLoadFailed`
            The given public key data was not a valid key.

        :exc:`SignatureVerifyFailed`
            The signature did not match the public key.

        Returns
        -------
        :class:`bytes`
            The verified message data
        """

        try:
            vk = VerifyKey(verify_key, encoder=HexEncoder)
            verified_message = vk.verify(message, HexEncoder.decode(signature), encoder=HexEncoder)

        except NACLValueError as e:
            log.error("verify_raw: public key failed")
            raise VerifyKeyLoadFailed("verify_raw invalid key", original=e) from e

        except BadSignatureError as e:
            log.error("verify_raw: signature failed")
            raise SignatureVerifyFailed("verify_raw signature bad", original=e) from e

        except Exception as e:
            log.error("verify_raw: other error")
            raise KeysignException("other error, probably bad signature", original=e) from e

        return verified_message

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LocalAccount):
            return NotImplemented
        return self._sign_key == other._sign_key and self._verify_key == other._verify_key

    def __repr__(self):
        return f"<LocalAccount(account_number={self.account_number})>"

    def __str__(self):
        return f"Account[{self.account_number.decode(encoding='utf-8')}]"
    
def is_valid_keypair(account_number: VerifyKey, signing_key: SigningKey) -> bool:
    return signing_key.verify_key == account_number


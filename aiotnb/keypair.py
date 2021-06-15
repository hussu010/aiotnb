"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("LocalAccount", "is_valid_keypair", "key_as_str", "AnyPubKey")

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Union, cast

from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from nacl.exceptions import ValueError as NACLValueError
from nacl.signing import SignedMessage, SigningKey, VerifyKey

from .errors import (
    KeyfileNotFound,
    KeysignException,
    SignatureVerifyFailed,
    SigningKeyLoadFailed,
    VerifyKeyLoadFailed,
)

_log = logging.getLogger(__name__)

AnyPubKey = Union[VerifyKey, bytes, str]


class LocalAccount:
    """
    Represents a local keypair account.

    .. admonition:: Supported Operations

        .. describe:: x == y
            Checks if the keypairs for both accounts are equal.

    Attributes
    ----------
    account_number: :class:`str`
        The network account number.
        The account number is the public key.

    account_number_bytes: :class:`bytes`
        The account number as hex-encoded bytes.

    signing_key:  :class:`str`
        The signing key for the account.
        The signing key is the **private** key.

        .. caution:: Do not share this key. This is the private key and can be used to impersonate you.

    signing_key_bytes: :class:`bytes`
        The account private key as hex-encoded bytes.


    """

    __slots__ = (
        "account_number",
        "account_number_bytes",
        "signing_key",
        "signing_key_bytes",
        "_sign_key",
        "_verify_key",
    )

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

        self.signing_key_bytes = private_key.encode(encoder=HexEncoder)
        self.signing_key = self.signing_key_bytes.decode("utf-8")

        self.account_number_bytes = self._verify_key.encode(encoder=HexEncoder)
        self.account_number = self.account_number_bytes.decode("utf-8")

    @classmethod
    def from_key_file(cls, key_file: Union[Path, str]) -> LocalAccount:
        """
        Load an account from an existing private key file.

        Parameters
        ----------
        key_file: Union[:class:`~pathlib.Path`, :class:`str`]
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
                _log.error("keyfile could not be read")
                raise KeysignException("keyfile could not be read", original=e) from e

        else:
            _log.error("keyfile path was not found")
            raise KeyfileNotFound(f"'{file_path.name}' was not found on the system")

        signing_key: SigningKey

        try:
            signing_key = SigningKey(raw_key, encoder=HexEncoder)

        except Exception as e:
            _log.error("private key load failed")
            raise SigningKeyLoadFailed("key must be 32 bytes long and hex-encoded", original=e) from e

        return cls(signing_key)

    @classmethod
    def generate(cls) -> LocalAccount:
        """
        Generates a new keypair and load an account from it.
        """

        return cls(SigningKey.generate())

    @classmethod
    def from_hex_string(cls, key: str) -> LocalAccount:
        """
        Returns a new keypair from the key.
        """
        try:
            return cls(SigningKey(key.encode(), encoder=HexEncoder))
        except Exception as e:
            _log.error("private key load failed")
            raise SigningKeyLoadFailed("key must be 32 bytes long and hex-encoded", original=e) from e


    def write_key_file(self, key_file: Union[Path, str]):
        """
        Write out the account's private key for safekeeping.

        Parameters
        ----------
        key_file_path: Union[:class:`~pathlib.Path`, :class:`str`]
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
                file_path.write_bytes(self.signing_key_bytes)

            except Exception as e:
                _log.error("keyfile write failed")
                raise KeysignException("keyfile could not be written", original=e) from e

        else:
            _log.error("keyfile already exists, not overwriting.")
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
        :class:`~nacl.signing.SignedMessage`
            The signature data.

        """

        return self._sign_key.sign(message, encoder=HexEncoder)

    @staticmethod
    def verify(signed_message: SignedMessage, verify_key: VerifyKey) -> bytes:
        """
        Takes a signed message, a signature, and a public key, and attempts to verify the signature on the message.

        Parameters
        ----------
        message: :class:`~nacl.signing.SignedMessage`
            The signed message + signature data.

        verify_key: :class:`~nacl.signing.VerifyKey`
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
            _log.error("verify: signature failed")
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
            _log.error("verify_raw: public key failed")
            raise VerifyKeyLoadFailed("verify_raw invalid key", original=e) from e

        except BadSignatureError as e:
            _log.error("verify_raw: signature failed")
            raise SignatureVerifyFailed("verify_raw signature bad", original=e) from e

        except Exception as e:
            _log.error("verify_raw: other error")
            raise KeysignException("other error, probably bad signature", original=e) from e

        return verified_message

    def __eq__(self, other: object):
        if not isinstance(other, LocalAccount):
            return NotImplemented

        return self._sign_key == other._sign_key and self._verify_key == other._verify_key

    def __repr__(self):
        return f"<LocalAccount(account_number={self.account_number})>"

    def __str__(self):
        return f"Account[{self.account_number}]"


def is_valid_keypair(account_number: bytes, signing_key: bytes) -> bool:
    """
    Takes an account_number, a signing_key and returns whether they are of the same keypair.

    Parameters
    ----------
    account_number: :class:`bytes`
        The account number of the keypair to validate.

    signing_key: :class:`bytes`
        The signing key of the keypair to validate.

    Raises
    ------
    :exc:`SigningKeyLoadFailed`
        The signing key was not a valid key.

    :exc:`VerifyKeyLoadFailed`
        The account number was not a valid key.

    Returns
    -------
    :class:`bool`
        The bool representing whether the keypair is valid.
    """
    try:
        sign_key = SigningKey(signing_key, encoder=HexEncoder)
    except Exception as e:
        _log.error("signing key load failed")
        raise SigningKeyLoadFailed("key must be 32 bytes long and valid", original=e) from e

    try:
        pub_key = VerifyKey(account_number, encoder=HexEncoder)
    except Exception as e:
        _log.error("accountnumber load failed")
        raise VerifyKeyLoadFailed("key must be 32 bytes long and valid", original=e) from e

    return sign_key.verify_key == pub_key


def key_as_str(key: AnyPubKey) -> str:
    """
    Takes a key of type AnyPubKey and converts it into a string.

    Parameters
    ----------
    key: :class:`AnyPubKey`
        The account number of the keypair to validate.

    Returns
    -------
    :class:`str`
        The string version of the key.
    """
    if type(key) == VerifyKey:
        new_key = cast(VerifyKey, key).encode(encoder=HexEncoder).decode("utf-8")

    elif type(key) is bytes:
        new_key = key.decode("utf-8")

    else:
        new_key = cast(str, key)

    return new_key

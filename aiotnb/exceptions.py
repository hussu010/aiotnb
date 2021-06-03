"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

from schema import SchemaError

__all__ = (
    "TNBException",
    "HTTPException",
    "Forbidden",
    "NotFound",
    "NetworkServerError",
    "ValidatorException",
    "KeysignException",
    "KeyfileNotFound",
    "SignatureVerifyFailed",
    "SigningKeyLoadFailed",
    "VerifyKeyLoadFailed",
)


from typing import TYPE_CHECKING, Any, Mapping, Optional

if TYPE_CHECKING:
    from aiohttp.client_reqrep import ClientResponse


class TNBException(Exception):
    """
    Root exception for aiotnb. Can be used to catch any library errors.
    """

    pass


# HTTP errors


class HTTPException(TNBException):
    """
    Base exception for any HTTP errors.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response from the failed request.

    text: :class:`str`
        Error message.

    status: :class:`int`
        HTTP status code of the response.
    """

    def __init__(self, response: ClientResponse, message: str):
        self.response = response
        self.message = message

        super().__init__(f"{response.status} {response.reason}: {message}")


class Forbidden(HTTPException):
    """
    Exception representing an HTTP 403 response.

    :class:`HTTPException` subclass.
    """

    pass


class NotFound(HTTPException):
    """
    Exception representing an HTTP 404 response.

    :class:`HTTPException` subclass.
    """

    pass


class NetworkServerError(HTTPException):
    """
    Exception representing an HTTP 503 response.

    :class:`HTTPException` subclass.
    """

    pass


# Validator errors


class ValidatorException(TNBException):
    """
    Base exception for any response validation errors.

    Attributes
    ----------
    data: Mapping[:class:`str`, Any]
        The response data that failed validation.

    original: :class:`SchemaError`
        The exception that was the direct cause of this one.

    message: :class:`str`
        Explanation of what went wrong while validating.`
    """

    def __init__(self, data: Mapping[str, Any], original: SchemaError):
        self.data = data
        self.original = original
        self.message = original.code


# LocalAccount errors


class KeysignException(TNBException):
    """
    Base exception for any key signing errors.

    Attributes
    ----------
    message: :class:`str`

    original: Optional[:class:`Exception`]
        The original exception that caused this one. May be ``None``.
    """

    def __init__(self, message: str, *, original: Optional[Exception] = None):
        self.message = message
        self.orignal = original


class KeyfileNotFound(KeysignException):
    """
    Exception indicating a specified private key file was not present.
    """

    pass


class SigningKeyLoadFailed(KeysignException):
    """
    Exception indicating a specified private key was not valid.
    """

    pass


class VerifyKeyLoadFailed(KeysignException):
    """
    Exception indicating a specified public key was not valid.
    """

    pass


class SignatureVerifyFailed(KeysignException):
    """
    Exception indicating a signature verification failed.
    """

    pass

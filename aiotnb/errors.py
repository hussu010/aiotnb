"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = (
    "TNBException",
    "IteratorEmpty",
    "HTTPException",
    "Unauthorized",
    "Forbidden",
    "NotFound",
    "NetworkServerError",
    "ValidatorException",
    "ValidatorTransformError",
    "ValidatorFailed",
    "KeysignException",
    "KeyfileNotFound",
    "SignatureVerifyFailed",
    "SigningKeyLoadFailed",
    "VerifyKeyLoadFailed",
)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

    from aiohttp.client_reqrep import ClientResponse


class TNBException(Exception):
    """
    Root exception for aiotnb. Can be used to catch any library errors.
    """

    pass


# Utility Errors


class IteratorEmpty(TNBException):
    """
    Indicates an iterator is exhausted. Only used because StopIteration does BadThings.
    """


# HTTP errors


class HTTPException(TNBException):
    """
    Base exception for any HTTP errors.

    Attributes
    ----------
    response: :class:`~aiohttp.ClientResponse`
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


class Unauthorized(HTTPException):
    """
    Represents an HTTP 401 response.
    """

    pass


class Forbidden(HTTPException):
    """
    Represents an HTTP 403 response.

    :class:`HTTPException` subclass.
    """

    pass


class NotFound(HTTPException):
    """
    Represents an HTTP 404 response.

    :class:`HTTPException` subclass.
    """

    pass


class NetworkServerError(HTTPException):
    """
    Represents an HTTP 503 response.

    :class:`HTTPException` subclass.
    """

    pass


# Validator errors


class ValidatorException(TNBException):
    """
    Base exception for any response validation errors.

    Attributes
    ----------
    message: :class:`str`
        Explanation of what went wrong while validating.`
    """

    def __init__(self, message: str):
        self.message = message


class ValidatorTransformError(ValidatorException):
    """
    Indicates a value could not be transformed while validating.
    """


class ValidatorFailed(ValidatorException):
    """
    Indicates a data validation did not succeed.
    """


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
    Indicates a specified private key file was not present.
    """

    pass


class SigningKeyLoadFailed(KeysignException):
    """
    Indicates a specified private key was not valid.
    """

    pass


class VerifyKeyLoadFailed(KeysignException):
    """
    Indicates a specified public key was not valid.
    """

    pass


class SignatureVerifyFailed(KeysignException):
    """
    Indicates a signature verification failed.
    """

    pass

"""
This type stub file was generated by pyright.
"""

class CryptoError(Exception):
    """
    Base exception for all nacl related errors
    """

    ...

class BadSignatureError(CryptoError):
    """
    Raised when the signature was forged or otherwise corrupt.
    """

    ...

class RuntimeError(RuntimeError, CryptoError): ...
class AssertionError(AssertionError, CryptoError): ...
class TypeError(TypeError, CryptoError): ...
class ValueError(ValueError, CryptoError): ...
class InvalidkeyError(CryptoError): ...
class CryptPrefixError(InvalidkeyError): ...

class UnavailableError(RuntimeError):
    """
    is a subclass of :class:`~nacl.exceptions.RuntimeError`, raised when
    trying to call functions not available in a minimal build of
    libsodium.
    """

    ...

def ensure(cond, *args, **kwds):
    """
    Return if a condition is true, otherwise raise a caller-configurable
    :py:class:`Exception`
    :param bool cond: the condition to be checked
    :param sequence args: the arguments to be passed to the exception's
                          constructor
    The only accepted named parameter is `raising` used to configure the
    exception to be raised if `cond` is not `True`
    """
    ...

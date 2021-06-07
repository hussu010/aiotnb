"""
This type stub file was generated by pyright.
"""

crypto_generichash_BYTES = ...
crypto_generichash_BYTES_MIN = ...
crypto_generichash_BYTES_MAX = ...
crypto_generichash_KEYBYTES = ...
crypto_generichash_KEYBYTES_MIN = ...
crypto_generichash_KEYBYTES_MAX = ...
crypto_generichash_SALTBYTES = ...
crypto_generichash_PERSONALBYTES = ...
crypto_generichash_STATEBYTES = ...
_OVERLONG = ...
_TOOBIG = ...

def generichash_blake2b_salt_personal(data, digest_size=..., key=..., salt=..., person=...):
    """One shot hash interface

    :param data: the input data to the hash function
    :param digest_size: must be at most
                        :py:data:`.crypto_generichash_BYTES_MAX`;
                        the default digest size is
                        :py:data:`.crypto_generichash_BYTES`
    :type digest_size: int
    :param key: must be at most
                :py:data:`.crypto_generichash_KEYBYTES_MAX` long
    :type key: bytes
    :param salt: must be at most
                 :py:data:`.crypto_generichash_SALTBYTES` long;
                 will be zero-padded if needed
    :type salt: bytes
    :param person: must be at most
                   :py:data:`.crypto_generichash_PERSONALBYTES` long:
                   will be zero-padded if needed
    :type person: bytes
    :return: digest_size long digest
    :rtype: bytes
    """
    ...

class Blake2State(object):
    """
    Python-level wrapper for the crypto_generichash_blake2b state buffer
    """

    __slots__ = ...
    def __init__(self, digest_size) -> None: ...
    def __reduce__(self):
        """
        Raise the same exception as hashlib's blake implementation
        on copy.copy()
        """
        ...
    def copy(self): ...

def generichash_blake2b_init(key=..., salt=..., person=..., digest_size=...):
    """
    Create a new initialized blake2b hash state

    :param key: must be at most
                :py:data:`.crypto_generichash_KEYBYTES_MAX` long
    :type key: bytes
    :param salt: must be at most
                 :py:data:`.crypto_generichash_SALTBYTES` long;
                 will be zero-padded if needed
    :type salt: bytes
    :param person: must be at most
                   :py:data:`.crypto_generichash_PERSONALBYTES` long:
                   will be zero-padded if needed
    :type person: bytes
    :param digest_size: must be at most
                        :py:data:`.crypto_generichash_BYTES_MAX`;
                        the default digest size is
                        :py:data:`.crypto_generichash_BYTES`
    :type digest_size: int
    :return: a initialized :py:class:`.Blake2State`
    :rtype: object
    """
    ...

def generichash_blake2b_update(state, data):
    """Update the blake2b hash state

    :param state: a initialized Blake2bState object as returned from
                     :py:func:`.crypto_generichash_blake2b_init`
    :type state: :py:class:`.Blake2State`
    :param data:
    :type data: bytes
    """
    ...

def generichash_blake2b_final(state):
    """Finalize the blake2b hash state and return the digest.

    :param state: a initialized Blake2bState object as returned from
                     :py:func:`.crypto_generichash_blake2b_init`
    :type state: :py:class:`.Blake2State`
    :return: the blake2 digest of the passed-in data stream
    :rtype: bytes
    """
    ...

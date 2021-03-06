"""
This type stub file was generated by pyright.
"""

crypto_secretstream_xchacha20poly1305_ABYTES = ...
crypto_secretstream_xchacha20poly1305_HEADERBYTES = ...
crypto_secretstream_xchacha20poly1305_KEYBYTES = ...
crypto_secretstream_xchacha20poly1305_MESSAGEBYTES_MAX = ...
crypto_secretstream_xchacha20poly1305_STATEBYTES = ...
crypto_secretstream_xchacha20poly1305_TAG_MESSAGE = ...
crypto_secretstream_xchacha20poly1305_TAG_PUSH = ...
crypto_secretstream_xchacha20poly1305_TAG_REKEY = ...
crypto_secretstream_xchacha20poly1305_TAG_FINAL = ...

def crypto_secretstream_xchacha20poly1305_keygen():
    """
    Generate a key for use with
    :func:`.crypto_secretstream_xchacha20poly1305_init_push`.

    """
    ...

class crypto_secretstream_xchacha20poly1305_state(object):
    """
    An object wrapping the crypto_secretstream_xchacha20poly1305 state.

    """

    __slots__ = ...
    def __init__(self) -> None:
        """Initialize a clean state object."""
        ...

def crypto_secretstream_xchacha20poly1305_init_push(state, key):
    """
    Initialize a crypto_secretstream_xchacha20poly1305 encryption buffer.

    :param state: a secretstream state object
    :type state: crypto_secretstream_xchacha20poly1305_state
    :param key: must be
                :data:`.crypto_secretstream_xchacha20poly1305_KEYBYTES` long
    :type key: bytes
    :return: header
    :rtype: bytes

    """
    ...

def crypto_secretstream_xchacha20poly1305_push(state, m, ad=..., tag=...):
    """
    Add an encrypted message to the secret stream.

    :param state: a secretstream state object
    :type state: crypto_secretstream_xchacha20poly1305_state
    :param m: the message to encrypt, the maximum length of an individual
              message is
              :data:`.crypto_secretstream_xchacha20poly1305_MESSAGEBYTES_MAX`.
    :type m: bytes
    :param ad: additional data to include in the authentication tag
    :type ad: bytes or None
    :param tag: the message tag, usually
                :data:`.crypto_secretstream_xchacha20poly1305_TAG_MESSAGE` or
                :data:`.crypto_secretstream_xchacha20poly1305_TAG_FINAL`.
    :type tag: int
    :return: ciphertext
    :rtype: bytes

    """
    ...

def crypto_secretstream_xchacha20poly1305_init_pull(state, header, key):
    """
    Initialize a crypto_secretstream_xchacha20poly1305 decryption buffer.

    :param state: a secretstream state object
    :type state: crypto_secretstream_xchacha20poly1305_state
    :param header: must be
                :data:`.crypto_secretstream_xchacha20poly1305_HEADERBYTES` long
    :type header: bytes
    :param key: must be
                :data:`.crypto_secretstream_xchacha20poly1305_KEYBYTES` long
    :type key: bytes

    """
    ...

def crypto_secretstream_xchacha20poly1305_pull(state, c, ad=...):
    """
    Read a decrypted message from the secret stream.

    :param state: a secretstream state object
    :type state: crypto_secretstream_xchacha20poly1305_state
    :param c: the ciphertext to decrypt, the maximum length of an individual
              ciphertext is
              :data:`.crypto_secretstream_xchacha20poly1305_MESSAGEBYTES_MAX` +
              :data:`.crypto_secretstream_xchacha20poly1305_ABYTES`.
    :type c: bytes
    :param ad: additional data to include in the authentication tag
    :type ad: bytes or None
    :return: (message, tag)
    :rtype: (bytes, int)

    """
    ...

def crypto_secretstream_xchacha20poly1305_rekey(state):
    """
    Explicitly change the encryption key in the stream.

    Normally the stream is re-keyed as needed or an explicit ``tag`` of
    :data:`.crypto_secretstream_xchacha20poly1305_TAG_REKEY` is added to a
    message to ensure forward secrecy, but this method can be used instead
    if the re-keying is controlled without adding the tag.

    :param state: a secretstream state object
    :type state: crypto_secretstream_xchacha20poly1305_state

    """
    ...

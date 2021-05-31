"""
This type stub file was generated by pyright.
"""

class EncryptedMessage(bytes):
    """
    A bytes subclass that holds a messaged that has been encrypted by a
    :class:`SecretBox`.
    """

    @property
    def nonce(self):
        """
        The nonce used during the encryption of the :class:`EncryptedMessage`.
        """
        ...
    @property
    def ciphertext(self):
        """
        The ciphertext contained within the :class:`EncryptedMessage`.
        """
        ...

class StringFixer(object):
    def __str__(self) -> str: ...

def bytes_as_string(bytes_in): ...
def random(size=...): ...
def randombytes_deterministic(size, seed, encoder=...):
    """
    Returns ``size`` number of deterministically generated pseudorandom bytes
    from a seed

    :param size: int
    :param seed: bytes
    :param encoder: The encoder class used to encode the produced bytes
    :rtype: bytes
    """
    ...

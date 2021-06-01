"""
This type stub file was generated by pyright.
"""

has_crypto_core_ed25519 = ...
crypto_core_ed25519_BYTES = ...
crypto_core_ed25519_SCALARBYTES = ...
crypto_core_ed25519_NONREDUCEDSCALARBYTES = ...
if has_crypto_core_ed25519:
    crypto_core_ed25519_BYTES = ...
    crypto_core_ed25519_SCALARBYTES = ...
    crypto_core_ed25519_NONREDUCEDSCALARBYTES = ...

def crypto_core_ed25519_is_valid_point(p):
    """
    Check if ``p`` represents a point on the edwards25519 curve, in canonical
    form, on the main subgroup, and that the point doesn't have a small order.

    :param p: a :py:data:`.crypto_core_ed25519_BYTES` long bytes sequence
              representing a point on the edwards25519 curve
    :type p: bytes
    :return: point validity
    :rtype: bool
    :raises nacl.exceptions.UnavailableError: If called when using a
        minimal build of libsodium.
    """
    ...

def crypto_core_ed25519_add(p, q):
    """
    Add two points on the edwards25519 curve.

    :param p: a :py:data:`.crypto_core_ed25519_BYTES` long bytes sequence
              representing a point on the edwards25519 curve
    :type p: bytes
    :param q: a :py:data:`.crypto_core_ed25519_BYTES` long bytes sequence
              representing a point on the edwards25519 curve
    :type q: bytes
    :return: a point on the edwards25519 curve represented as
             a :py:data:`.crypto_core_ed25519_BYTES` long bytes sequence
    :rtype: bytes
    :raises nacl.exceptions.UnavailableError: If called when using a
        minimal build of libsodium.
    """
    ...

def crypto_core_ed25519_sub(p, q):
    """
    Subtract a point from another on the edwards25519 curve.

    :param p: a :py:data:`.crypto_core_ed25519_BYTES` long bytes sequence
              representing a point on the edwards25519 curve
    :type p: bytes
    :param q: a :py:data:`.crypto_core_ed25519_BYTES` long bytes sequence
              representing a point on the edwards25519 curve
    :type q: bytes
    :return: a point on the edwards25519 curve represented as
             a :py:data:`.crypto_core_ed25519_BYTES` long bytes sequence
    :rtype: bytes
    :raises nacl.exceptions.UnavailableError: If called when using a
        minimal build of libsodium.
    """
    ...

def crypto_core_ed25519_scalar_invert(s):
    """
    Return the multiplicative inverse of integer ``s`` modulo ``L``,
    i.e an integer ``i`` such that ``s * i = 1 (mod L)``, where ``L``
    is the order of the main subgroup.

    Raises a ``exc.RuntimeError`` if ``s`` is the integer zero.

    :param s: a :py:data:`.crypto_core_ed25519_SCALARBYTES`
              long bytes sequence representing an integer
    :type s: bytes
    :return: an integer represented as a
              :py:data:`.crypto_core_ed25519_SCALARBYTES` long bytes sequence
    :rtype: bytes
    :raises nacl.exceptions.UnavailableError: If called when using a
        minimal build of libsodium.
    """
    ...

def crypto_core_ed25519_scalar_negate(s):
    """
    Return the integer ``n`` such that ``s + n = 0 (mod L)``, where ``L``
    is the order of the main subgroup.

    :param s: a :py:data:`.crypto_core_ed25519_SCALARBYTES`
              long bytes sequence representing an integer
    :type s: bytes
    :return: an integer represented as a
              :py:data:`.crypto_core_ed25519_SCALARBYTES` long bytes sequence
    :rtype: bytes
    :raises nacl.exceptions.UnavailableError: If called when using a
        minimal build of libsodium.
    """
    ...

def crypto_core_ed25519_scalar_complement(s):
    """
    Return the complement of integer ``s`` modulo ``L``, i.e. an integer
    ``c`` such that ``s + c = 1 (mod L)``, where ``L`` is the order of
    the main subgroup.

    :param s: a :py:data:`.crypto_core_ed25519_SCALARBYTES`
              long bytes sequence representing an integer
    :type s: bytes
    :return: an integer represented as a
              :py:data:`.crypto_core_ed25519_SCALARBYTES` long bytes sequence
    :rtype: bytes
    :raises nacl.exceptions.UnavailableError: If called when using a
        minimal build of libsodium.
    """
    ...

def crypto_core_ed25519_scalar_add(p, q):
    """
    Add integers ``p`` and ``q`` modulo ``L``, where ``L`` is the order of
    the main subgroup.

    :param p: a :py:data:`.crypto_core_ed25519_SCALARBYTES`
              long bytes sequence representing an integer
    :type p: bytes
    :param q: a :py:data:`.crypto_core_ed25519_SCALARBYTES`
              long bytes sequence representing an integer
    :type q: bytes
    :return: an integer represented as a
              :py:data:`.crypto_core_ed25519_SCALARBYTES` long bytes sequence
    :rtype: bytes
    :raises nacl.exceptions.UnavailableError: If called when using a
        minimal build of libsodium.
    """
    ...

def crypto_core_ed25519_scalar_sub(p, q):
    """
    Subtract integers ``p`` and ``q`` modulo ``L``, where ``L`` is the
    order of the main subgroup.

    :param p: a :py:data:`.crypto_core_ed25519_SCALARBYTES`
              long bytes sequence representing an integer
    :type p: bytes
    :param q: a :py:data:`.crypto_core_ed25519_SCALARBYTES`
              long bytes sequence representing an integer
    :type q: bytes
    :return: an integer represented as a
              :py:data:`.crypto_core_ed25519_SCALARBYTES` long bytes sequence
    :rtype: bytes
    :raises nacl.exceptions.UnavailableError: If called when using a
        minimal build of libsodium.
    """
    ...

def crypto_core_ed25519_scalar_mul(p, q):
    """
    Multiply integers ``p`` and ``q`` modulo ``L``, where ``L`` is the
    order of the main subgroup.

    :param p: a :py:data:`.crypto_core_ed25519_SCALARBYTES`
              long bytes sequence representing an integer
    :type p: bytes
    :param q: a :py:data:`.crypto_core_ed25519_SCALARBYTES`
              long bytes sequence representing an integer
    :type q: bytes
    :return: an integer represented as a
              :py:data:`.crypto_core_ed25519_SCALARBYTES` long bytes sequence
    :rtype: bytes
    :raises nacl.exceptions.UnavailableError: If called when using a
        minimal build of libsodium.
    """
    ...

def crypto_core_ed25519_scalar_reduce(s):
    """
    Reduce integer ``s`` to ``s`` modulo ``L``, where ``L`` is the order
    of the main subgroup.

    :param s: a :py:data:`.crypto_core_ed25519_NONREDUCEDSCALARBYTES`
              long bytes sequence representing an integer
    :type s: bytes
    :return: an integer represented as a
              :py:data:`.crypto_core_ed25519_SCALARBYTES` long bytes sequence
    :rtype: bytes
    :raises nacl.exceptions.UnavailableError: If called when using a
        minimal build of libsodium.
    """
    ...
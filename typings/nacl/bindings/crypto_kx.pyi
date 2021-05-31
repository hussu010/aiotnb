"""
This type stub file was generated by pyright.
"""

crypto_kx_PUBLIC_KEY_BYTES = ...
crypto_kx_SECRET_KEY_BYTES = ...
crypto_kx_SEED_BYTES = ...
crypto_kx_SESSION_KEY_BYTES = ...

def crypto_kx_keypair():
    """
    Generate a keypair.
    This is a duplicate crypto_box_keypair, but
    is included for api consistency.
    :return: (public_key, secret_key)
    :rtype: (bytes, bytes)
    """
    ...

def crypto_kx_seed_keypair(seed):
    """
    Generate a keypair with a given seed.
    This is functionally the same as crypto_box_seed_keypair, however
    it uses the blake2b hash primitive instead of sha512.
    It is included mainly for api consistency when using crypto_kx.
    :param seed: random seed
    :type seed: bytes
    :return: (public_key, secret_key)
    :rtype: (bytes, bytes)
    """
    ...

def crypto_kx_client_session_keys(client_public_key, client_secret_key, server_public_key):
    """
    Generate session keys for the client.
    :param client_public_key:
    :type client_public_key: bytes
    :param client_secret_key:
    :type client_secret_key: bytes
    :param server_public_key:
    :type server_public_key: bytes
    :return: (rx_key, tx_key)
    :rtype: (bytes, bytes)
    """
    ...

def crypto_kx_server_session_keys(server_public_key, server_secret_key, client_public_key):
    """
    Generate session keys for the server.
    :param server_public_key:
    :type server_public_key: bytes
    :param server_secret_key:
    :type server_secret_key: bytes
    :param client_public_key:
    :type client_public_key: bytes
    :return: (rx_key, tx_key)
    :rtype: (bytes, bytes)
    """
    ...

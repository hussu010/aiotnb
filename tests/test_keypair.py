"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from typing import cast

import pytest
from nacl.encoding import HexEncoder
from nacl.signing import SignedMessage

from aiotnb.core import LocalAccount, is_valid_keypair

keypair_1 = LocalAccount.generate()
keypair_2 = LocalAccount.generate()

MESSAGE = "THIS IS-A TEST[!@]"
stored_message = None


@pytest.mark.order(before="test_write_load")
def test_repr(capsys):
    with capsys.disabled():
        print(keypair_1, end=" ")
        print(keypair_2, end="")

    assert True


def test_write_load(tmp_path):
    output = tmp_path / "private_1.key"
    keypair_1.write_key_file(output)

    test_keypair_1 = LocalAccount.from_key_file(output)

    assert test_keypair_1 == keypair_1


def test_write_raw(tmp_path):
    output = tmp_path / "private_2.key"

    keypair_2.write_key_file(output)

    data = output.read_bytes()

    assert data == keypair_2.signing_key


def test_sign():
    signature = keypair_2.sign_message(MESSAGE)
    message = keypair_2.verify(MESSAGE, signature, keypair_2.account_number)

    assert message == MESSAGE


def test_is_valid_keypair():
    assert is_valid_keypair(keypair_1.account_number, keypair_1.signing_key)


@pytest.mark.xfail
@pytest.mark.order(after="test_is_valid_keypair")
def test_is_not_valid_keypair():
    assert is_valid_keypair(
        b"8e8efdaa4cf11f8350720d29c8cef0c6fda728c822ba03fa5e2533416dd03ff5",
        keypair_1.signing_key,
    )

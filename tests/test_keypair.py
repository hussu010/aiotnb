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

MESSAGE = b"THIS IS-A TEST[!@]"
stored_message = None


@pytest.mark.order(before="test_write_load")
def test_repr(capsys):
    with capsys.disabled():
        print()
        print(keypair_1)
        print(keypair_2)

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


@pytest.mark.order(before="test_sign_load")
def test_sign_store():
    global stored_message

    stored_message = keypair_1.sign_message(MESSAGE)

    assert stored_message.message == HexEncoder.encode(MESSAGE)


def test_sign_load():
    message = keypair_2.verify(cast(SignedMessage, stored_message), keypair_1._verify_key)

    assert message == MESSAGE


@pytest.mark.order(after="test_sign_load")
def test_sign_load_raw():
    message = keypair_2.verify_raw(HexEncoder.encode(MESSAGE), stored_message.signature, keypair_1.account_number)

    assert message == MESSAGE


def test_is_valid_keypair():
    assert is_valid_keypair(
        HexEncoder.decode(keypair_1.account_number), HexEncoder.decode(keypair_1.signing_key)
    )
    assert not is_valid_keypair(
        bytes.fromhex("8e8efdaa4cf11f8350720d29c8cef0c6fda728c822ba03fa5e2533416dd03ff5"),
        HexEncoder.decode(keypair_1.signing_key),
    )

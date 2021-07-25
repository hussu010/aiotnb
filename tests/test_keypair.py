"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from typing import cast

import pytest
from nacl.signing import SignedMessage

from aiotnb.keypair import Keypair, is_valid_keypair

keypair_1 = Keypair.generate()
keypair_2 = Keypair.generate()

MESSAGE = b"THIS IS-A TEST[!@]"
stored_message = None


def test_write_load(tmp_path):
    output = tmp_path / "private_1.key"
    keypair_1.write_key_file(output)

    test_keypair_1 = Keypair.from_key_file(output)

    assert test_keypair_1 == keypair_1


def test_write_raw(tmp_path):
    output = tmp_path / "private_2.key"

    keypair_2.write_key_file(output)

    data = output.read_bytes()

    assert data.decode("utf-8") == keypair_2.signing_key


@pytest.mark.order(before="test_sign_load")
def test_sign_store():
    global stored_message

    stored_message = keypair_1.sign_message(MESSAGE)

    assert stored_message.message == MESSAGE


def test_sign_load():
    message = keypair_2.verify(cast(SignedMessage, stored_message), keypair_1._verify_key)

    assert message == MESSAGE


@pytest.mark.order(after="test_sign_load")
def test_sign_load_raw():
    message = keypair_2.verify_raw(MESSAGE, stored_message.signature, keypair_1.account_number)

    assert message == MESSAGE


def test_is_valid_keypair():
    assert is_valid_keypair(keypair_1.account_number, keypair_1.signing_key)


@pytest.mark.xfail
@pytest.mark.order(after="test_is_valid_keypair")
def test_is_not_valid_keypair():
    assert is_valid_keypair(
        "8e8efdaa4cf11f8350720d29c8cef0c6fda728c822ba03fa5e2533416dd03ff5",
        keypair_1.signing_key,
    )

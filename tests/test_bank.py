"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

import pytest

from aiotnb import Bank, connect_to_bank
from aiotnb.common import BankTransaction, Block, PaginatedResponse

pytestmark = pytest.mark.asyncio


async def test_node_cache(bank: Bank):
    new_bank = await connect_to_bank("54.177.121.3")

    assert bank.node_identifier_bytes == new_bank.node_identifier_bytes


async def test_primary_validator_fetch(bank: Bank):
    assert bank.primary_validator is not None


async def test_transaction_fetch(bank: Bank):
    txi = await bank.fetch_transactions(limit=3)

    assert isinstance(txi, PaginatedResponse)

    tx = await txi.next()

    assert isinstance(tx, BankTransaction)

    assert isinstance(tx.block, Block)


async def test_fetch_banks(bank: Bank):
    # This may fail at some point with more nodes
    # Keep an eye on it
    banks = await bank.fetch_banks()
    banks = await banks.flatten()

    assert banks[0].node_identifier == bank.node_identifier

"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from datetime import datetime

import pytest

from aiotnb import Bank, connect_to_bank
from aiotnb.common import BankTransaction, Block, PaginatedResponse

pytestmark = pytest.mark.asyncio


async def test_core_connect(bank: Bank):
    new_bank = await connect_to_bank("54.183.16.194")

    assert bank._node_identifier == new_bank._node_identifier, "NID equality check failed"

    # this should fail, because we're creating a new state with a new cache
    # assert bank is new_bank, "Identity check failed"


async def test_accounts_list(bank: Bank):
    accs = await bank.fetch_accounts()

    assert await accs.next()


async def test_transactions_list(bank: Bank):
    txi = await bank.fetch_transactions()

    assert await txi.next()


async def test_banks_list(bank: Bank):
    # This may fail at some point with more nodes
    # Keep an eye on it
    banks = await bank.fetch_banks()

    assert await banks.next()


async def test_blocks_list(bank: Bank):
    blocks = await bank.fetch_blocks()

    assert await blocks.next()


async def test_clean_status(bank: Bank):
    c_stat, c_time = await bank.clean_status()

    if c_stat is not None:
        assert isinstance(c_stat, str)

    if c_time is not None:
        assert isinstance(c_time, datetime)


async def test_node_cache_2(bank: Bank):
    new_bank = await bank.fetch_config()

    assert bank._node_identifier == new_bank._node_identifier, "NID equality check failed"
    assert bank is new_bank, "Identity check failed"


async def test_confirmation_blocks_list(bank: Bank):
    blocks = await bank.fetch_confirmation_blocks()

    assert await blocks.next()


async def test_crawl_status(bank: Bank):
    c_stat, c_time = await bank.crawl_status()

    if c_stat is not None:
        assert isinstance(c_stat, str)

    if c_time is not None:
        assert isinstance(c_time, datetime)


@pytest.mark.xfail(strict=True)
async def test_invalid_blocks_empty(bank: Bank):
    iv_block_iter = await bank.fetch_invalid_blocks()

    await iv_block_iter.next()


async def test_confirmation_services_list(bank: Bank):
    svcs = await bank.fetch_confirmation_services()

    assert await svcs.next()


async def test_validator_list(bank: Bank):
    vs = await bank.fetch_validators()

    assert await vs.next()


# async def test_validator_by_nid(bank: Bank):
#     v = await bank.fetch_validator_by_nid(b"9375feb25085c6f2a58640404e7c16582e210a6a12717c8d3d5307f750c861fc")

#     assert v

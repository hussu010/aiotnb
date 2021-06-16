"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

import asyncio

import pytest

import aiotnb

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()

    yield loop

    loop.close()


@pytest.fixture(scope="module")
async def client():
    client = aiotnb.http.HTTPClient()  # type: ignore

    await client.init_session()

    yield client

    await client.close()


@pytest.fixture(scope="module")
async def bank():
    bank = await aiotnb.connect_to_bank("54.177.121.3")

    # return bank
    yield bank

    await bank._state.close()

"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from datetime import datetime
from typing import Optional, Type, Union, cast

import pytest
from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from schema import And
from schema import Optional as sOptional
from schema import Or, Schema, Use
from yarl import URL

from aiotnb import ISO8601UTCTimestamp, validate_with

pytestmark = pytest.mark.asyncio


@validate_with(Schema({}))
async def unchanged_data():
    return {}


async def test_unchanged():
    result = await unchanged_data()

    assert result == {}


@validate_with(Schema({"timestamp": ISO8601UTCTimestamp(error="bad timestamp")}))
async def timestamp_data(stamp: str):
    return {"timestamp": stamp}


async def test_iso_timestamp():
    result = await timestamp_data("2020-10-08T02:18:07.346849Z")

    assert result == dict(timestamp=datetime(2020, 10, 8, 2, 18, 7, 346849))


complex_schema = Schema(
    {
        "count": int,
        "next": Or(None, And(Use(URL))),
        "previous": Or(None, And(Use(URL))),
        "results": [
            {
                "id": str,
                "created_date": ISO8601UTCTimestamp(),
                "modified_date": ISO8601UTCTimestamp(),
                "account_number": And(str, Use(lambda s: VerifyKey(s.encode("utf-8"), encoder=HexEncoder))),
                "trust": And(str, Use(float)),
            }
        ],
    }
)


@validate_with(complex_schema)
async def complex_data():
    return {
        "count": 87,
        "next": "http://143.110.137.54/accounts?limit=2&offset=2",
        "previous": None,
        "results": [
            {
                "id": "5a8c7990-393a-4299-ae92-2f096a2c7f43",
                "created_date": "2020-10-08T02:18:07.346849Z",
                "modified_date": "2020-10-08T02:18:07.346914Z",
                "account_number": "a37e2836805975f334108b55523634c995bd2a4db610062f404510617e83126f",
                "trust": "0.00",
            },
            {
                "id": "2682963f-06b1-47d7-a2e1-1f8ec6ae98dc",
                "created_date": "2020-10-08T02:39:44.071810Z",
                "modified_date": "2020-10-08T02:39:44.071853Z",
                "account_number": "cc8fb4ebbd2b9a98a767e801ac2b0d296ced88b5d3b7d6d6e12e1d2d7635d724",
                "trust": "2.38",
            },
        ],
    }


async def test_complex():
    result = await complex_data()

    test_data = {
        "count": 87,
        "next": URL("http://143.110.137.54/accounts?limit=2&offset=2"),
        "previous": None,
        "results": [
            {
                "id": "5a8c7990-393a-4299-ae92-2f096a2c7f43",
                "created_date": datetime(2020, 10, 8, 2, 18, 7, 346849),
                "modified_date": datetime(2020, 10, 8, 2, 18, 7, 346914),
                "account_number": VerifyKey(
                    b"\xa3~(6\x80Yu\xf34\x10\x8bUR64\xc9\x95\xbd*M\xb6\x10\x06/@E\x10a~\x83\x12o"
                ),
                "trust": 0.0,
            },
            {
                "id": "2682963f-06b1-47d7-a2e1-1f8ec6ae98dc",
                "created_date": datetime(2020, 10, 8, 2, 39, 44, 71810),
                "modified_date": datetime(2020, 10, 8, 2, 39, 44, 71853),
                "account_number": VerifyKey(
                    b"\xcc\x8f\xb4\xeb\xbd+\x9a\x98\xa7g\xe8\x01\xac+\r)l\xed\x88\xb5\xd3\xb7\xd6\xd6\xe1.\x1d-v5\xd7$"
                ),
                "trust": 2.38,
            },
        ],
    }

    assert result == test_data

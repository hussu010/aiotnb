"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

import pytest

from aiotnb.exceptions import Forbidden, HTTPException, NetworkServerError, NotFound
from aiotnb.http_client import HTTPClient, HTTPMethod, Route

pytestmark = pytest.mark.asyncio


@pytest.fixture  # type: ignore
async def client():
    c = HTTPClient()
    await c._init_session()

    yield c

    await c.close()


def test_route():
    r = Route(HTTPMethod.Post, "/a/b/c")

    assert r.resolve("http://example.com") == ("POST", "http://example.com/a/b/c")


def test_route_param():
    d = {"bank_id": "test-node", "useless": 0}

    r = Route(HTTPMethod.Get, "/banks/{bank_id}", **d)

    assert r.resolve("http://test.bank.site") == ("GET", f"http://test.bank.site/banks/test-node")


async def test_get(client):
    payload = {"test": "yes"}
    route = Route(HTTPMethod.Get, "/get")

    result = await client.request(route.resolve("https://httpbin.org"), params=payload)

    assert result["args"] == payload


async def test_post(client):
    payload = {"test": "yes"}
    params = {"test": "also yes"}
    route = Route(HTTPMethod.Post, "/post")

    result = await client.request(route.resolve("https://httpbin.org"), params=params, json=payload)

    assert result["json"] == payload and result["args"] == params


async def test_put(client):
    payload = {"test": "yes"}
    params = {"test": "also yes"}
    route = Route(HTTPMethod.Put, "/put")

    result = await client.request(route.resolve("https://httpbin.org"), params=params, json=payload)

    assert result["json"] == payload and result["args"] == params


async def test_patch(client):
    payload = {"test": "yes"}
    params = {"test": "also yes"}
    route = Route(HTTPMethod.Patch, "/patch")

    result = await client.request(route.resolve("https://httpbin.org"), params=params, json=payload)

    assert result["json"] == payload and result["args"] == params


async def test_delete(client):
    payload = {"test": "yes"}
    params = {"test": "also yes"}
    route = Route(HTTPMethod.Delete, "/delete")

    result = await client.request(route.resolve("https://httpbin.org"), params=params, json=payload)

    assert result["json"] == payload and result["args"] == params


async def test_403(client):
    payload = {"code": 403}

    route = Route(HTTPMethod.Get, "/status/{code}", **payload)

    try:
        await client.request(route.resolve("https://httpbin.org"))

    except Exception as e:
        assert isinstance(e, Forbidden)


async def test_404(client):
    payload = {"code": 404}

    route = Route(HTTPMethod.Get, "/status/{code}", **payload)

    try:
        await client.request(route.resolve("https://httpbin.org"))

    except Exception as e:
        assert isinstance(e, NotFound)


async def test_503(client):
    payload = {"code": 503}

    route = Route(HTTPMethod.Get, "/status/{code}", **payload)

    try:
        await client.request(route.resolve("https://httpbin.org"))

    except Exception as e:
        assert isinstance(e, NetworkServerError)


async def test_502(client):
    payload = {"code": 502}

    route = Route(HTTPMethod.Get, "/status/{code}", **payload)

    try:
        await client.request(route.resolve("https://httpbin.org"))

    except Exception as e:
        assert isinstance(e, HTTPException)


# class TestBasicHTTP:
#     @classmethod
#     def setup_class(cls):
#         cls.client = HTTPClient()

#     @pytest.mark.order(1)
#     async def test_setup(self, loop):
#         await self.client._init_session()

#         assert self.client._session is not None

#     @pytest.mark.order(2)
#     async def test_get(self):
#         # await self.client._session._loop.close()
#         # self.client._session._loop = loop
#         loop = asyncio.get_running_loop()
#         self.client._session._loop = loop
#         payload = {"test": "yes"}
#         route = Route(HTTPMethod.Get, "/get")

#         result = await asyncio.wait_for(
#             asyncio.shield(self.client.request(route.resolve("https://httpbin.org"), params=payload)), None
#         )

#         assert result["args"] == payload

#     @pytest.mark.order(3)
#     async def test_shutdown(self):
#         await self.client.close()

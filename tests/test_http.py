"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

import pytest
from yarl import URL

from aiotnb.exceptions import Forbidden, HTTPException, NetworkServerError, NotFound
from aiotnb.http import HTTPClient, HTTPMethod, Route

pytestmark = pytest.mark.asyncio


@pytest.fixture  # type: ignore
async def client():
    c = HTTPClient()
    await c.init_session()

    yield c

    await c.close()


def test_route():
    r = Route(HTTPMethod.post, "a/b/c")

    assert r.resolve(URL("http://example.com")) == ("POST", URL("http://example.com/a/b/c"))


def test_route_param():
    d = {"bank_id": "test-node", "useless": 0}

    r = Route(HTTPMethod.get, "banks/{bank_id}", **d)

    assert r.resolve(URL("http://test.bank.site")) == ("GET", URL("http://test.bank.site/banks/test-node"))


async def test_get(client):
    payload = {"test": "yes"}
    route = Route(HTTPMethod.get, "get")

    result = await client.request(route.resolve(URL("https://httpbin.org")), params=payload)

    assert result["args"] == payload


async def test_post(client):
    payload = {"test": "yes"}
    params = {"test": "also yes"}
    route = Route(HTTPMethod.post, "post")

    result = await client.request(route.resolve(URL("https://httpbin.org")), params=params, json=payload)

    assert result["json"] == payload and result["args"] == params


async def test_put(client):
    payload = {"test": "yes"}
    params = {"test": "also yes"}
    route = Route(HTTPMethod.put, "put")

    result = await client.request(route.resolve(URL("https://httpbin.org")), params=params, json=payload)

    assert result["json"] == payload and result["args"] == params


async def test_patch(client):
    payload = {"test": "yes"}
    params = {"test": "also yes"}
    route = Route(HTTPMethod.patch, "patch")

    result = await client.request(route.resolve(URL("https://httpbin.org")), params=params, json=payload)

    assert result["json"] == payload and result["args"] == params


async def test_delete(client):
    payload = {"test": "yes"}
    params = {"test": "also yes"}
    route = Route(HTTPMethod.delete, "delete")

    result = await client.request(route.resolve(URL("https://httpbin.org")), params=params, json=payload)

    assert result["json"] == payload and result["args"] == params


async def test_403(client):
    payload = {"code": 403}

    route = Route(HTTPMethod.get, "status/{code}", **payload)

    try:
        await client.request(route.resolve(URL("https://httpbin.org")))

    except Exception as e:
        assert isinstance(e, Forbidden)


async def test_404(client):
    payload = {"code": 404}

    route = Route(HTTPMethod.get, "status/{code}", **payload)

    try:
        await client.request(route.resolve(URL("https://httpbin.org")))

    except Exception as e:
        assert isinstance(e, NotFound)


async def test_503(client):
    payload = {"code": 503}

    route = Route(HTTPMethod.get, "status/{code}", **payload)

    try:
        await client.request(route.resolve(URL("https://httpbin.org")))

    except Exception as e:
        assert isinstance(e, NetworkServerError)


async def test_502(client):
    payload = {"code": 502}

    route = Route(HTTPMethod.get, "status/{code}", **payload)

    try:
        await client.request(route.resolve(URL("https://httpbin.org")))

    except Exception as e:
        assert isinstance(e, HTTPException)

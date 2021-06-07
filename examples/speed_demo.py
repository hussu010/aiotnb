# Copyright (c) 2021 AnonymousDapper

# type: ignore

import asyncio
import time

from tnb import banks, validators
from yarl import URL

import aiotnb
from aiotnb import HTTPClient, HTTPMethod, Route

BANK_ADDRESS = "54.177.121.3"


async def aiotnb_test():
    client = HTTPClient()
    await client.init_session()

    route = Route(HTTPMethod.Get, "validators").resolve(URL(f"http://{BANK_ADDRESS}"))
    results = await client.request(route)

    node_list = []
    for validator in results["results"]:
        route = Route(HTTPMethod.Get, "/config").resolve(f"http://{validator['ip_address']}")

        node_result = await client.request(route)
        node_list.append(node_result["node_type"])

    await client.close()

    return node_list


def tnb_test():
    bank = banks.Bank(address=BANK_ADDRESS)

    result = bank.fetch_validators(limit=100)

    node_list = []
    for validator in result["results"]:
        validator_obj = validators.Validator(address=validator["ip_address"], port=validator["port"])

        node_result = validator_obj.fetch_validator_config()
        node_list.append(node_result["node_type"])

    return node_list


if __name__ == "__main__":
    # test old client
    start_1 = time.monotonic()
    result_1 = tnb_test()
    end_1 = time.monotonic()

    # test new client
    start_2 = time.monotonic()
    result_2 = asyncio.run(aiotnb_test())
    end_2 = time.monotonic()

    diff_1 = end_1 - start_1
    diff_2 = end_2 - start_2

    print(f"[tnb]    Gathered {len(result_1)} validator nodes in {(diff_1 * 1000):.4f}ms")
    print(f"[aiotnb] Gathered {len(result_2)} validator nodes in {(diff_2 * 1000):.4f}ms")

    if diff_1 > diff_2:
        print(f"[aiotnb] Faster by {((diff_1 / diff_2) - 1) * 100:.0f}%")
    else:
        print(f"[tnb] Faster by {((diff_2 / diff_1) - 1) * 100:.0f}%")

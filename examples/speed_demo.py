# Copyright (c) 2021 AnonymousDapper

# type: ignore

import asyncio
import logging
import time

from tnb import banks
from yarl import URL

import aiotnb
from aiotnb import connect_to_bank
from aiotnb.enums import AccountOrder

BANK_ADDRESS = "54.183.16.194"


logging.basicConfig(level=logging.INFO)


async def aiotnb_test():
    bank = await connect_to_bank(BANK_ADDRESS)

    account_iter = await bank.fetch_accounts(ordering=AccountOrder.trust_desc, page_limit=10)

    result = await account_iter.flatten()

    await bank._state.close()

    return result


def tnb_test():
    bank = banks.Bank(address=BANK_ADDRESS)

    offset = 0
    done = False

    node_list = []
    while not done:
        result = bank.fetch_accounts(offset=offset, limit=10)

        if result["next"]:
            offset = URL(result["next"]).query["offset"]
        else:
            done = True

        node_list += result["results"]

    return node_list


if __name__ == "__main__":
    # test old client
    start_1 = time.perf_counter()
    result_1 = tnb_test()
    end_1 = time.perf_counter()

    # test new client
    start_2 = time.perf_counter()
    result_2 = asyncio.run(aiotnb_test())
    end_2 = time.perf_counter()

    diff_1 = end_1 - start_1
    diff_2 = end_2 - start_2

    print(f"[tnb]    Gathered {len(result_1)} accounts (10-per-page) in {(diff_1 * 1000):.4f}ms")
    print(f"[aiotnb] Gathered {len(result_2)} accounts (10-per-page) in {(diff_2 * 1000):.4f}ms")

    if diff_1 > diff_2:
        print(f"[aiotnb] Faster by {((diff_1 / diff_2) - 1) * 100:.0f}%")
    else:
        print(f"[tnb] Faster by {((diff_2 / diff_1) - 1) * 100:.0f}%")

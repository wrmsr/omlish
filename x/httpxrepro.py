#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "~=3.13.9"
# dependencies = ["httpx==0.28.1"]
# ///
"""
!! Only happens under pycharm/pydevd debugger on asyncio !!

It's probably pydevd_nest_asyncio. It's always pydevd_nest_asyncio.

====

Exception ignored in: <async_generator object HTTP11ConnectionByteStream.__aiter__ at 0x12aca5e40>
Traceback (most recent call last):
  File "/Users/spinlock/src/wrmsr/omlish/.venvs/default/lib/python3.13/site-packages/httpcore/_async/connection_pool.py", line 404, in __aiter__
    yield part
RuntimeError: async generator ignored GeneratorExit

====

Notes:
 - Traced to:
  - HTTP11ConnectionByteStream.aclose -> await self._connection._response_closed()
  - AsyncHTTP11Connection._response_closed -> async with self._state_lock
  - anyio._backends._asyncio.Lock.acquire -> await AsyncIOBackend.cancel_shielded_checkpoint() -> await sleep(0)
 - https://github.com/encode/httpx/discussions/2963
  - Exception ignored in: <async_generator object HTTP11ConnectionByteStream.__aiter__ at 0x1325a7540>
  - RuntimeError: async generator ignored GeneratorExit
"""
import asyncio

import httpx


async def _a_main() -> None:
    async with httpx.AsyncClient() as client:
        async with client.stream(method='GET', url='https://httpbin.org/stream/10') as resp:
            async for b in resp.aiter_bytes():
                print(b)
                break


if __name__ == '__main__':
    asyncio.run(_a_main())

import asyncio
import contextlib

import httpx


async def _a_main() -> None:
    async with contextlib.AsyncExitStack() as es:
        client = await es.enter_async_context(httpx.AsyncClient())

        resp = await es.enter_async_context(client.stream(
            method='GET',
            url='https://google.com/',
        ))
        
        it = resp.aiter_bytes()

        @es.push_async_callback
        async def close_it() -> None:
            try:
                # print(f'close_it.begin: {it=}', file=sys.stderr)
                await it.aclose()  # type: ignore[attr-defined]
                # print(f'close_it.end: {it=}', file=sys.stderr)
            except BaseException as be:  # noqa
                # print(f'close_it.__exit__: {it=} {be=}', file=sys.stderr)
                raise
            finally:
                # print(f'close_it.finally: {it=}', file=sys.stderr)
                pass

        async def read1(n: int = -1, /) -> bytes:
            try:
                return await anext(it)
            except StopAsyncIteration:
                return b''

        while b := await read1():
            print(b)
            break


if __name__ == '__main__':
    asyncio.run(_a_main())

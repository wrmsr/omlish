import asyncio

import httpx


async def _a_main() -> None:
    async with httpx.AsyncClient() as client:
        async with client.stream(method='GET', url='https://google.com/') as resp:
            async for b in resp.aiter_bytes():
                print(b)
                break


if __name__ == '__main__':
    asyncio.run(_a_main())

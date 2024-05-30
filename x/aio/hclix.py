import asyncio

import httpx


async def _a_main():
    async with httpx.AsyncClient() as client:
        r = await client.get('https://www.example.com/')
        print(r)


if __name__ == '__main__':
    asyncio.run(_a_main())

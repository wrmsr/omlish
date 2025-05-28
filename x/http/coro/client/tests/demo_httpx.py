import asyncio

import httpx


async def _a_main() -> None:
    async def stream_response(url):
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', url) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    print(chunk.decode('utf-8'), end='')

    for url in [
        'http://www.example.com',
        'https://www.baidu.com',
        'https://anglesharp.azurewebsites.net/Chunked',
    ]:
        await stream_response(url)


if __name__ == '__main__':
    asyncio.run(_a_main())

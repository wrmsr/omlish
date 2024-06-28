"""
https://cloud.lambdalabs.com/api/v1/docs

https://docs.lambdalabs.com/on-demand-cloud/cloud-api

curl -u "$LAMBDALABS_API_KEY:" https://cloud.lambdalabs.com/api/v1/instance-types
"""
import asyncio

from omlish import json
import aiohttp

from ....secrets import load_secrets


async def _a_main() -> None:
    cfg = load_secrets()

    async with aiohttp.ClientSession(
        auth=aiohttp.BasicAuth(cfg['lambda_labs_api_key']),
    ) as session:
        async with session.get('https://cloud.lambdalabs.com/api/v1/instances') as resp:
            print(resp.status)
            buf = await resp.text()
            print(json.dumps_pretty(json.loads(buf)))


if __name__ == '__main__':
    asyncio.run(_a_main())

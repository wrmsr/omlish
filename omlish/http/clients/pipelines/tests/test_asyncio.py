"""
TODO:
 - axes:
   - flow
   - ssl : 'https://example.com/'
   - gzip decompress : 'https://httpbingo.org/gzip'
   - gzip compressed
"""
from .....testing.unittest.asyncs import AsyncioIsolatedAsyncTestCase
from ...base import HttpClientRequest
from ..asyncio import AsyncioIoPipelineAsyncHttpClient


class TestAsyncioClient(AsyncioIsolatedAsyncTestCase):
    async def test_simple(self):
        async with AsyncioIoPipelineAsyncHttpClient() as client:
            async with (await client.stream_request(HttpClientRequest(
                'http://example.com/',
            ))) as resp:
                print(resp)
                print(await resp.stream.readall())

    async def test_ssl(self):
        async with AsyncioIoPipelineAsyncHttpClient() as client:
            async with (await client.stream_request(HttpClientRequest(
                    'https://example.com/',
            ))) as resp:
                print(resp)
                print(await resp.stream.readall())

    async def test_gzip(self):
        async with AsyncioIoPipelineAsyncHttpClient() as client:
            async with (await client.stream_request(HttpClientRequest(
                    'http://example.com/gzip',
            ))) as resp:
                print(resp)
                print(await resp.stream.readall())

    async def test_ssl_gzip(self):
        async with AsyncioIoPipelineAsyncHttpClient() as client:
            async with (await client.stream_request(HttpClientRequest(
                    'https://example.com/gzip',
            ))) as resp:
                print(resp)
                print(await resp.stream.readall())

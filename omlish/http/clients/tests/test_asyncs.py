import asyncio
import concurrent.futures as cf
import contextlib

import pytest

from .. import default
from ..base import HttpClientError
from ..base import HttpClientRequest
from ..base import StatusHttpClientError
from ..executor import ExecutorAsyncHttpClient
from ..httpx import HttpxAsyncHttpClient
from ..middleware import MiddlewareAsyncHttpClient
from ..middleware import RedirectHandlingHttpClientMiddleware
from ..pipelines.asyncio import AsyncioIoPipelineAsyncHttpClient
from ..syncasync import SyncAsyncHttpClient
from ..urllib import UrllibHttpClient


@contextlib.asynccontextmanager
async def thread_executor_urllib_async_http_client():
    loop = asyncio.get_running_loop()
    with cf.ThreadPoolExecutor() as executor:
        with UrllibHttpClient() as client:
            async with ExecutorAsyncHttpClient(
                    lambda *args: loop.run_in_executor(executor, *args),  # noqa
                    client,
            ) as acli:
                yield acli


@contextlib.asynccontextmanager
async def sync_async_urllib_async_http_client():
    with UrllibHttpClient() as client:
        yield SyncAsyncHttpClient(client)


@contextlib.asynccontextmanager
async def middleware_pipeline_async_http_client():
    async with AsyncioIoPipelineAsyncHttpClient() as client0:
        async with MiddlewareAsyncHttpClient(
                client0,
                [
                    RedirectHandlingHttpClientMiddleware(),
                ],
        ) as client1:
            yield client1


CLIENTS: list = [
    HttpxAsyncHttpClient,
    thread_executor_urllib_async_http_client,
    sync_async_urllib_async_http_client,
    middleware_pipeline_async_http_client,
]


@pytest.mark.asyncs('asyncio')
@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
@pytest.mark.parametrize('data', [None, '{}', b'{}'])
async def test_clients(cls, data):
    async with cls() as cli:
        resp = await cli.request(HttpClientRequest(
            f'https://httpbingo.org/{"post" if data else "get"}',
            'POST' if data is not None else 'GET',
            headers={'User-Agent': 'omlish'},
            data=data,
        ))
        print(resp)
        assert resp.status == 200


@pytest.mark.asyncs('asyncio')
@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
@pytest.mark.parametrize('data', [None, '{}', b'{}'])
@pytest.mark.parametrize('readall', [False, True])
async def test_clients_stream(cls, data, readall):
    async with cls() as cli:
        async with (await cli.stream_request(HttpClientRequest(
                'https://httpbingo.org/drip?duration=1&numbytes=10&code=200&delay=1',
                'POST' if data is not None else 'GET',
                headers={'User-Agent': 'omlish'},
                data=data,
        ))) as resp:
            print(resp)
            assert resp.status == 200

            if readall:
                data = await resp.stream.read()
            else:
                l = []
                while (b := await resp.stream.read1(1)):
                    l.append(b)
                data = b''.join(l)

            assert data == b'**********'


@pytest.mark.asyncs('asyncio')
@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
async def test_clients_error(cls):
    data = None
    async with cls() as cli:
        resp = await cli.request(HttpClientRequest(
            'https://httpbingo.org/basic-auth/foo/bar',
            'POST' if data is not None else 'GET',
            headers={'User-Agent': 'omlish'},
            data=data,
        ))
        print(resp)
        assert resp.status == 401


@pytest.mark.asyncs('asyncio')
@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
async def test_clients_error_check(cls):
    data = None
    async with cls() as cli:
        with pytest.raises(StatusHttpClientError) as ex:
            await cli.request(
                HttpClientRequest(
                    'https://httpbingo.org/basic-auth/foo/bar',
                    'POST' if data is not None else 'GET',
                    headers={'User-Agent': 'omlish'},
                    data=data,
                ),
                check=True,
            )
        assert ex.value.response.status == 401


@pytest.mark.asyncs('asyncio')
@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
async def test_clients_error_url(cls):
    data = None
    async with cls() as cli:
        with pytest.raises(HttpClientError):
            await cli.request(HttpClientRequest(
                'https://foo.notarealtld/',
                'POST' if data is not None else 'GET',
                headers={'User-Agent': 'omlish'},
                data=data,
            ))


@pytest.mark.asyncs('asyncio')
@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
@pytest.mark.parametrize('data', [None, '{}', b'{}'])
async def test_default(cls, data):
    async with cls() as cli:
        resp = await default.async_request(
            f'https://httpbingo.org/{"post" if data is not None else "get"}',
            'POST' if data is not None else 'GET',
            headers={'User-Agent': 'omlish'},
            data=data,
            client=cli,
        )
        print(resp)
        assert resp.status == 200

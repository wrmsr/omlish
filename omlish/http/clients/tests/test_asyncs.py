import pytest

from .. import default
from ..base import HttpClientError
from ..base import HttpRequest
from ..base import HttpStatusError
from ..httpx import HttpxAsyncHttpClient


CLIENTS: list = [HttpxAsyncHttpClient]


@pytest.mark.asyncs('asyncio')
@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
@pytest.mark.parametrize('data', [None, '{}', b'{}'])
async def test_clients(cls, data):
    async with cls() as cli:
        resp = await cli.request(HttpRequest(
            'https://httpbun.org/',
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
@pytest.mark.parametrize('read_all', [False, True])
async def test_clients_stream(cls, data, read_all):
    async with cls() as cli:
        async with (await cli.stream_request(HttpRequest(
                'https://httpbun.org/drip?duration=1&numbytes=10&code=200&delay=1',
                'POST' if data is not None else 'GET',
                headers={'User-Agent': 'omlish'},
                data=data,
        ))) as resp:
            print(resp)
            assert resp.status == 200

            if read_all:
                data = await resp.read_all()
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
        resp = await cli.request(HttpRequest(
            'https://httpbun.org/basic-auth/foo/bar',
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
        with pytest.raises(HttpStatusError) as ex:
            await cli.request(
                HttpRequest(
                    'https://httpbun.org/basic-auth/foo/bar',
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
            await cli.request(HttpRequest(
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
            'https://httpbun.org/',
            'POST' if data is not None else 'GET',
            headers={'User-Agent': 'omlish'},
            data=data,
            client=cli,
        )
        print(resp)
        assert resp.status == 200

import contextlib
import urllib.parse

import pytest

from .. import default
from ..base import HttpClientError
from ..base import HttpRequest
from ..base import HttpStatusError
from ..coro.sync import CoroHttpClient
from ..httpx import HttpxHttpClient
from ..middleware import MiddlewareHttpClient
from ..middleware import RedirectHandlingHttpClientMiddleware
from ..urllib import UrllibHttpClient


@contextlib.contextmanager
def middleware_coro_http_client():
    with CoroHttpClient() as client0:
        with MiddlewareHttpClient(
                client0,
                [
                    RedirectHandlingHttpClientMiddleware(),
                ],
        ) as client1:
            yield client1


CLIENTS: list = [
    UrllibHttpClient,
    HttpxHttpClient,
    middleware_coro_http_client,
]


@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
@pytest.mark.parametrize('data', [None, '{}', b'{}'])
def test_clients(cls, data):
    with cls() as cli:
        resp = cli.request(HttpRequest(
            'https://httpbun.org/',
            'POST' if data is not None else 'GET',
            headers={'User-Agent': 'omlish'},
            data=data,
        ))
        print(resp)
        assert resp.status == 200


@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
@pytest.mark.parametrize('data', [None, '{}', b'{}'])
@pytest.mark.parametrize('readall', [False, True])
def test_clients_stream(cls, data, readall):
    with cls() as cli:
        with cli.stream_request(HttpRequest(
            'https://httpbun.org/drip?duration=1&numbytes=10&code=200&delay=1',
            'POST' if data is not None else 'GET',
            headers={'User-Agent': 'omlish'},
            data=data,
        )) as resp:
            print(resp)
            assert resp.status == 200

            if readall:
                data = resp.readall()
            else:
                l = []
                while (b := resp.stream.read1(1)):
                    l.append(b)
                data = b''.join(l)

            assert data == b'**********'


@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
def test_clients_error(cls):
    data = None
    with cls() as cli:
        resp = cli.request(HttpRequest(
            'https://httpbun.org/basic-auth/foo/bar',
            'POST' if data is not None else 'GET',
            headers={'User-Agent': 'omlish'},
            data=data,
        ))
        print(resp)
        assert resp.status == 401


@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
def test_clients_error_check(cls):
    data = None
    with cls() as cli:
        with pytest.raises(HttpStatusError) as ex:
            cli.request(
                HttpRequest(
                    'https://httpbun.org/basic-auth/foo/bar',
                    'POST' if data is not None else 'GET',
                    headers={'User-Agent': 'omlish'},
                    data=data,
                ),
                check=True,
            )
        assert ex.value.response.status == 401


@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
def test_clients_error_url(cls):
    data = None
    with cls() as cli:
        with pytest.raises(HttpClientError):
            cli.request(HttpRequest(
                'https://foo.notarealtld/',
                'POST' if data is not None else 'GET',
                headers={'User-Agent': 'omlish'},
                data=data,
            ))


@pytest.mark.online
@pytest.mark.parametrize('cls', [c for c in CLIENTS if c is not HttpxHttpClient])
@pytest.mark.parametrize('abs', [False, True])
def test_clients_redirect(cls, abs):  # noqa
    with cls() as cli:
        resp = cli.request(
            HttpRequest(
                f'https://httpbun.org/redirect-to?{urllib.parse.urlencode({"url": "https://httpbun.org/html"})}' if abs else  # noqa
                'https://httpbun.org/redirect?url=html',
                headers={'User-Agent': 'omlish'},
            ),
            check=True,
        )
        assert resp.status == 200
        assert resp.headers.single_str_dct['content-type'].split(';')[0] == 'text/html'
        assert resp.data


@pytest.mark.online
@pytest.mark.parametrize('cls', CLIENTS)
@pytest.mark.parametrize('data', [None, '{}', b'{}'])
def test_default(cls, data):
    with cls() as cli:
        resp = default.request(
            'https://httpbun.org/',
            'POST' if data is not None else 'GET',
            headers={'User-Agent': 'omlish'},
            data=data,
            client=cli,
        )
        print(resp)
        assert resp.status == 200

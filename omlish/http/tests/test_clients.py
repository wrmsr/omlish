import pytest

from ..clients import HttpClientError
from ..clients import HttpRequest
from ..clients import HttpStatusError
from ..clients import HttpxHttpClient
from ..clients import UrllibHttpClient


@pytest.mark.online
@pytest.mark.parametrize('cls', [UrllibHttpClient, HttpxHttpClient])
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
@pytest.mark.parametrize('cls', [UrllibHttpClient, HttpxHttpClient])
@pytest.mark.parametrize('data', [None, '{}', b'{}'])
@pytest.mark.parametrize('read_all', [False, True])
def test_clients_stream(cls, data, read_all):
    with cls() as cli:
        with cli.stream_request(HttpRequest(
            'https://httpbun.org/drip?duration=1&numbytes=10&code=200&delay=1',
            'POST' if data is not None else 'GET',
            headers={'User-Agent': 'omlish'},
            data=data,
        )) as resp:
            print(resp)
            assert resp.status == 200

            if read_all:
                data = resp.stream.read()
            else:
                l = []
                while (b := resp.stream.read(1)):
                    l.append(b)
                data = b''.join(l)

            assert data == b'**********'


@pytest.mark.online
@pytest.mark.parametrize('cls', [UrllibHttpClient, HttpxHttpClient])
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
@pytest.mark.parametrize('cls', [UrllibHttpClient, HttpxHttpClient])
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
@pytest.mark.parametrize('cls', [UrllibHttpClient, HttpxHttpClient])
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

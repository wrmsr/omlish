import pytest

from ..clients import HttpRequest
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

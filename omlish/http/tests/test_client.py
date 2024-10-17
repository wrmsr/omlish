import pytest

from ..client import HttpRequest
from ..client import HttpxHttpClient
from ..client import UrllibHttpClient


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

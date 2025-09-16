import pytest

from ....clients.base import HttpRequest
from .clientimpl import CoroHttpClientHttpClient


@pytest.skip('FIXME')
@pytest.mark.online
@pytest.mark.parametrize('data', [None, '{}', b'{}'])
@pytest.mark.parametrize('read_all', [False, True])
def test_clients_stream(data, read_all):
    with CoroHttpClientHttpClient() as cli:
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

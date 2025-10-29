import pytest

from ...base import HttpRequest
from ..sync import CoroHttpClient


# @pytest.skip('FIXME')
@pytest.mark.online
@pytest.mark.parametrize('data', [None, '{}', b'{}'])
@pytest.mark.parametrize('readall', [False, True])
def test_clients_stream(data, readall):
    with CoroHttpClient() as cli:
        with cli.stream_request(HttpRequest(
                'https://httpbun.org/drip?duration=1&numbytes=10&code=200&delay=1',
                'POST' if data is not None else 'GET',
                headers={'User-Agent': 'omlish'},
                data=data,
        )) as resp:
            print(resp)
            assert resp.status == 200

            if readall:
                data = resp.stream.readall()
            else:
                l = []
                while (b := resp.stream.read1(1)):
                    l.append(b)
                data = b''.join(l)

            assert data == b'**********'


@pytest.mark.online
def test_get_zombo():
    from ....clients.default import request
    from ....clients.httpx import HttpxHttpClient  # noqa
    from ....clients.urllib import UrllibHttpClient  # noqa

    print(request(
        'https://zombo.com/',
        client=CoroHttpClient(),
        # client=HttpxHttpClient(),
        # client=UrllibHttpClient(),
    ).data)

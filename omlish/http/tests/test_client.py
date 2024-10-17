import pytest

from ..client import HttpRequest
from ..client import HttpxHttpClient
from ..client import UrllibHttpClient


@pytest.mark.online
def test_clients():
    for cls in [
        UrllibHttpClient,
        HttpxHttpClient,
    ]:
        with cls() as cli:
            resp = cli.request(HttpRequest(
                'https://www.google.com',
                headers={'User-Agent': 'omlish'},
            ))
            print(resp)

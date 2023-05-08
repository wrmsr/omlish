import urllib.request

import pytest

from .. import client as client_


@pytest.mark.xfail()
def test_client():
    with urllib.request.urlopen('http://www.python.org/') as f:
        print(f.read(300))

    c = client_.UrllibHttpClient()
    with c.request(client_.HttpRequest('http://www.python.org/')) as f:
        print(f.read(300))

import pytest

from omlish import lang
from omlish.http import all as http
from omlish.secrets.tests.harness import HarnessSecrets

from .....services import Request
from ..search import CseSearchService


@pytest.mark.online
def test_search(harness):
    sec = harness[HarnessSecrets]
    cse_id = sec.get_or_skip('google_cse_id')
    cse_api_key = sec.get_or_skip('google_cse_api_key')

    res = lang.sync_await(CseSearchService(
        cse_id=cse_id.reveal(),
        cse_api_key=cse_api_key.reveal(),
        http_client=http.SyncAsyncHttpClient(http.client()),
    ).invoke(Request('lectures')))

    print(res)
    assert res.v

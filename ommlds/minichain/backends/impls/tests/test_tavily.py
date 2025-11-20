import pytest

from omlish import lang
from omlish.http import all as http
from omlish.secrets.tests.harness import HarnessSecrets

from ....registries.globals import registry_new
from ....search import SearchService
from ....services import Request
from ....standard import ApiKey
from ..tavily import TavilySearchService


@pytest.mark.skip_unless_alone
@pytest.mark.online
def test_search(harness):
    svc = TavilySearchService(
        ApiKey(harness[HarnessSecrets].get_or_skip('tavily_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

    res = lang.sync_await(svc.invoke(Request('the disco biscuits')))

    print(res)
    assert res


def test_manifest():
    svc = registry_new(SearchService, 'tavily')
    assert isinstance(svc, TavilySearchService)

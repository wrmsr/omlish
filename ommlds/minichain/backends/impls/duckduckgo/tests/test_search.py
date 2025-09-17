import ddgs.exceptions
import pytest

from omlish import lang
from omlish.testing import pytest as ptu

from .....registries.globals import registry_new
from .....search import SearchService
from .....services import Request
from ..search import DuckduckgoSearchService


@ptu.skip.if_cant_import('ddgs')
@pytest.mark.online
def test_search():
    try:
        res = lang.sync_await(DuckduckgoSearchService().invoke(Request('the disco biscuits')))
    except (ddgs.exceptions.RatelimitException, TimeoutError) as e:
        print(e)
        return

    print(res)
    assert res


@ptu.skip.if_cant_import('ddgs')
def test_manifest():
    svc = registry_new(SearchService, 'ddg')
    assert isinstance(svc, DuckduckgoSearchService)

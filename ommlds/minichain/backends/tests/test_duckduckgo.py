import typing as ta

import pytest

from omlish import lang
from omlish.testing import pytest as ptu

from ...registry import registry_new
from ...search import SearchService
from ...services import Request
from ..duckduckgo import DuckduckgoSearchService


if ta.TYPE_CHECKING:
    import ddgs
else:
    ddgs = lang.proxy_import('ddgs')


@ptu.skip.if_cant_import('ddgs')
@pytest.mark.online
def test_search():
    try:
        res = DuckduckgoSearchService().invoke(Request('the disco biscuits'))
    except (ddgs.exceptions.RatelimitException, TimeoutError) as e:
        print(e)
        return

    print(res)
    assert res


@ptu.skip.if_cant_import('ddgs')
def test_manifest():
    svc = registry_new(SearchService, 'ddg')  # type: ignore[type-abstract]
    assert isinstance(svc, DuckduckgoSearchService)

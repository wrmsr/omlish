import typing as ta

import pytest

from omlish import lang
from omlish.testing import pytest as ptu

from ...search import SearchService
from ..duckduckgo import DuckduckgoSearchService
from ..manifests import new_backend


if ta.TYPE_CHECKING:
    import duckduckgo_search
else:
    duckduckgo_search = lang.proxy_import('duckduckgo_search')


@ptu.skip.if_cant_import('duckduckgo_search')
@pytest.mark.online
def test_search():
    try:
        res = DuckduckgoSearchService()('the disco biscuits')
    except (duckduckgo_search.exceptions.RatelimitException, TimeoutError) as e:
        print(e)
        return

    print(res)
    assert res


@ptu.skip.if_cant_import('duckduckgo_search')
def test_manifest():
    svc = new_backend(SearchService, 'ddg')  # type: ignore[type-abstract]
    assert isinstance(svc, DuckduckgoSearchService)

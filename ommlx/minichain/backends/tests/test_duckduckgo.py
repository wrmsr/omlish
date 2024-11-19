import pytest

from omlish.testing import pytest as ptu

from ..duckduckgo import DuckduckgoSearchService


@ptu.skip.if_cant_import('duckduckgo_search')
@pytest.mark.online
def test_search():
    res = DuckduckgoSearchService()('the disco biscuits')

    print(res)
    assert res

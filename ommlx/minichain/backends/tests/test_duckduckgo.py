import pytest

from ..duckduckgo import DuckduckgoSearchService


@pytest.mark.online
def test_search():
    res = DuckduckgoSearchService()('the disco biscuits')

    print(res)
    assert res

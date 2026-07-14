import pytest

from ....search import Request
from ....search import SearchHit
from ....search import SearchHits
from ....search import SearchResponse
from ....search import static_check_is_search_service
from ....tools.execution.permissions import StaticToolPermissionDecider
from ....tools.permissions.types import ToolPermissionState
from ..fetching import DictWebFetcher
from ..fetching import FetchedPage
from ..fetching import html_to_text
from ..tools.fetch import WebFetchTool
from ..tools.search import WebSearchTool


def _allow() -> StaticToolPermissionDecider:
    return StaticToolPermissionDecider(ToolPermissionState.ALLOW)


def test_html_to_text():
    out = html_to_text(
        '<html><head><title>t</title><style>x{}</style></head>'
        '<body><h1>Hello</h1><script>ignore()</script><p>World here</p></body></html>',
    )
    assert 'Hello' in out
    assert 'World here' in out
    assert 'ignore()' not in out
    assert 'x{}' not in out


@pytest.mark.asyncs('asyncio')
async def test_web_fetch_tool_cleans_html_and_gates_permission():
    fetcher = DictWebFetcher({
        'https://example.com': FetchedPage(
            'https://example.com', 200,
            b'<html><body><h1>Doc Title</h1><p>Body text.</p></body></html>',
        ),
    })

    tool = WebFetchTool(
        fetcher=fetcher,
        tool_permission_decider=_allow(),
    )

    out = await tool.web_fetch('https://example.com')
    assert 'Doc Title' in out
    assert 'Body text.' in out
    assert '<' not in out  # tags stripped


@pytest.mark.asyncs('asyncio')
async def test_web_fetch_denied_by_default():
    fetcher = DictWebFetcher({})
    tool = WebFetchTool(fetcher=fetcher)  # default decider denies

    with pytest.raises(Exception):  # noqa
        await tool.web_fetch('https://example.com')


@static_check_is_search_service
class _DictSearchService:
    def __init__(self, hits_by_query):
        super().__init__()
        self._hits_by_query = hits_by_query

    async def invoke(self, request: Request) -> SearchResponse:
        return SearchResponse(SearchHits(l=self._hits_by_query.get(request.v, [])))


@pytest.mark.asyncs('asyncio')
async def test_web_search_tool():
    svc = _DictSearchService({
        'disco biscuits': [
            SearchHit(title='The Disco Biscuits', url='https://example.com/db', description='A band.'),
        ],
    })
    tool = WebSearchTool(search_service=svc)

    out = await tool.web_search('disco biscuits')
    assert 'The Disco Biscuits' in out
    assert 'https://example.com/db' in out
    assert 'A band.' in out

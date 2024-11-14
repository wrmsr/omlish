import typing as ta

from omlish import lang

from ..search import SearchHit
from ..search import SearchHits
from ..search import SearchRequest
from ..search import SearchResponse
from ..search import SearchService


if ta.TYPE_CHECKING:
    import duckduckgo_search
else:
    duckduckgo_search = lang.proxy_import('duckduckgo_search')


class DuckduckgoSearchService(SearchService):
    def invoke(
            self,
            request: SearchRequest,
    ) -> SearchResponse:
        ddgs = duckduckgo_search.DDGS()
        res = ddgs.text(request.v)
        return SearchResponse(v=SearchHits(
            l=[
                SearchHit(
                    title=d.get('title'),
                    url=d.get('href'),
                    description=d.get('description'),
                    snippets=[body] if (body := d.get('body')) is not None else None,
                )
                for d in res
            ],
        ))

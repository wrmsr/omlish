"""
https://developers.google.com/custom-search/vo1/reference/rest/v1/cse/list?apix=true
https://developers.google.com/custom-search/v1/reference/rest/v1/Search
https://google.aip.dev/127
"""
import typing as ta
import urllib.parse

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json
from omlish.http import all as http

from ...search import SearchHit
from ...search import SearchHits
from ...search import SearchRequest
from ...search import SearchResponse
from ...search import SearchService


##


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
class CseSearchResult(lang.Final):
    kind: str | None = None

    title: str | None = None
    html_title: str | None = None

    link: str | None = None
    display_link: str | None = None

    snippet: str | None = None
    html_snippet: str | None = None

    cache_id: str | None = None

    formatted_url: str | None = None
    html_formatted_url: str | None = None

    mime: str | None = None
    file_format: str | None = None

    x: ta.Mapping[str, ta.Any] | None = dc.field(default=None, repr=False)


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
class CseSearchInfo(lang.Final):
    search_time: float | None = None
    total_results: int | None = None

    x: ta.Mapping[str, ta.Any] | None = dc.field(default=None, repr=False)


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
class CseSearchResponse(lang.Final):
    kind: str | None = None
    info: CseSearchInfo | None = dc.xfield(None) | msh.update_field_metadata(name='searchInformation')
    items: ta.Sequence[CseSearchResult] | None = None

    x: ta.Mapping[str, ta.Any] | None = dc.field(default=None, repr=False)


class CseSearchService(SearchService):
    def __init__(
            self,
            cse_id: str | None = None,
            cse_api_key: str | None = None,
    ) -> None:
        super().__init__()

        self._cse_id = cse_id
        self._cse_api_key = cse_api_key

    def invoke(
            self,
            request: SearchRequest,
    ) -> SearchResponse:
        qs = urllib.parse.urlencode(dict(
            key=check.non_empty_str(self._cse_api_key),
            cx=check.non_empty_str(self._cse_id),
            q=request.query,
        ))
        resp = http.request(
            f'https://www.googleapis.com/customsearch/v1?{qs}',
        )
        out = check.not_none(resp.data)

        dct = json.loads(out.decode('utf-8'))
        res = msh.unmarshal(dct, CseSearchResponse)
        return SearchResponse(SearchHits(
            l=[
                SearchHit(
                    title=i.title,
                    url=i.link,
                    snippets=[i.snippet],
                )
                for i in res.items or ()
            ],
            total_results=res.info.total_results if res.info is not None else None,
        ))

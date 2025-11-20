from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http

from ....backends.tavily import protocol as pt
from ...search import SearchHit
from ...search import SearchHits
from ...search import SearchRequest
from ...search import SearchResponse
from ...search import static_check_is_search_service
from ...standard import ApiKey


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='tavily',
#     type='SearchService',
# )
@static_check_is_search_service
class TavilySearchService:
    def __init__(
            self,
            *configs: ApiKey,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client

        with tv.consume(*configs) as cc:
            self._api_key = ApiKey.pop_secret(cc, env='TAVILY_API_KEY')

    async def invoke(self, request: SearchRequest) -> SearchResponse:
        pt_request = pt.SearchRequest(
            query=request.v,
        )

        raw_request = msh.marshal(pt_request)

        http_response = await http.async_request(
            'https://api.tavily.com/search',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
            client=self._http_client,
        )

        raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))

        pt_response = msh.unmarshal(raw_response, pt.SearchResponse)

        return SearchResponse(SearchHits(
            l=[
                SearchHit(
                    title=r.title,
                    url=r.url,
                )
                for r in pt_response.results or []
            ],
        ))

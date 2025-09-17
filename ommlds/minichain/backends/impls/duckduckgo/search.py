import ddgs

from ....search import SearchHit
from ....search import SearchHits
from ....search import SearchRequest
from ....search import SearchResponse
from ....search import static_check_is_search_service


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='duckduckgo',
#     aliases=['ddg'],
#     type='SearchService',
# )
@static_check_is_search_service
class DuckduckgoSearchService:
    async def invoke(self, request: SearchRequest) -> SearchResponse:
        dsch = ddgs.DDGS()
        res = dsch.text(request.v)
        return SearchResponse(SearchHits(
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

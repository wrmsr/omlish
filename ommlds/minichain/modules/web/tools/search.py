import io
import typing as ta

from ....search import Request
from ....search import SearchService


##


MAX_SEARCH_RESULTS: ta.Final = 10


class WebFetchToolError(Exception):
    pass


class WebSearchTool:
    def __init__(
            self,
            *,
            search_service: SearchService,
            max_search_results: int | None = None,
    ) -> None:
        super().__init__()

        self._search_service = search_service
        if max_search_results is None:
            max_search_results = MAX_SEARCH_RESULTS
        self._max_search_results = max_search_results

    async def web_search(
            self,
            query: str,
    ) -> str:
        """
        Searches the web and returns a list of result titles, urls, and snippets.

        Args:
            query: The search query.
        """

        hits = (await self._search_service.invoke(Request(query))).v

        out = io.StringIO()
        out.write('<results>\n')
        for h in list(hits.l)[:MAX_SEARCH_RESULTS]:
            out.write(f'- {h.title or "(untitled)"}\n')
            if h.url:
                out.write(f'  {h.url}\n')
            for sn in (h.snippets or ([h.description] if h.description else [])):
                out.write(f'  {sn}\n')
        out.write('</results>\n')

        return out.getvalue()

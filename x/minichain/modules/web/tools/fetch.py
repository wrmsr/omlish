import typing as ta

from ....tools.execution.permissions import DENY_TOOL_PERMISSION_DECIDER
from ....tools.execution.permissions import ToolPermissionDecider
from ....tools.permissions.url import UrlToolPermissionTarget
from ..fetching import WebFetcher
from ..fetching import page_to_text


##


DEFAULT_MAX_CHARS: ta.Final = 50_000


class WebFetchToolError(Exception):
    pass


class WebFetchTool:
    def __init__(
            self,
            *,
            fetcher: WebFetcher,
            tool_permission_decider: ToolPermissionDecider = DENY_TOOL_PERMISSION_DECIDER,
            max_chars: int | None = None,
    ) -> None:
        super().__init__()

        self._fetcher = fetcher
        self._tool_permission_decider = tool_permission_decider
        if max_chars is None:
            max_chars = DEFAULT_MAX_CHARS
        self._max_chars = max_chars

    async def web_fetch(
            self,
            url: str,
    ) -> str:
        """
        Fetches a web page and returns its content as text (HTML is reduced to readable text).

        Args:
            url: The absolute URL to fetch.
        """

        await self._tool_permission_decider.check_allowed(UrlToolPermissionTarget(url, method='GET'))

        page = await self._fetcher.fetch(url)
        if not (200 <= page.status < 300):
            raise WebFetchToolError(f'fetching {url!r} returned HTTP {page.status}')

        text = page_to_text(page)
        if len(text) > self._max_chars:
            text = text[:self._max_chars] + '\n... (truncated)'
        return text

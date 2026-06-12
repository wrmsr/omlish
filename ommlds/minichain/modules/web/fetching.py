import abc
import html.parser
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.http import all as http


##


@dc.dataclass(frozen=True)
class FetchedPage(lang.Final):
    url: str
    status: int
    body: bytes


class WebFetcher(lang.Abstract):
    @abc.abstractmethod
    def fetch(self, url: str) -> ta.Awaitable[FetchedPage]:
        raise NotImplementedError


class HttpWebFetcher(WebFetcher):
    def __init__(
            self,
            *,
            http_client: http.AsyncHttpClient | None = None,
            timeout_s: float = 30.,
    ) -> None:
        super().__init__()

        self._http_client = http_client
        self._timeout_s = timeout_s

    async def fetch(self, url: str) -> FetchedPage:
        resp = await http.async_request(
            url,
            client=self._http_client,
            timeout_s=self._timeout_s,
        )
        data = resp.data
        body = data.encode('utf-8') if isinstance(data, str) else (data or b'')
        return FetchedPage(url, resp.status, body)


class DictWebFetcher(WebFetcher):
    """A canned fetcher (URL -> page) - the no-network test impl, and a useful cache/fixture in its own right."""

    def __init__(self, pages: ta.Mapping[str, FetchedPage]) -> None:
        super().__init__()

        self._pages = dict(pages)

    async def fetch(self, url: str) -> FetchedPage:
        try:
            return self._pages[url]
        except KeyError:
            return FetchedPage(url, 404, b'')


##


class _HtmlTextExtractor(html.parser.HTMLParser):
    _SKIP_TAGS: ta.AbstractSet[str] = frozenset(['script', 'style', 'head'])

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)

        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: ta.Any) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth and (s := data.strip()):
            self._parts.append(s)

    def text(self) -> str:
        return '\n'.join(self._parts)


def looks_like_html(text: str) -> bool:
    low = text.lower()
    return '<!doctype html' in low or '<html' in low or '<body' in low or low.count('</') > 2


def html_to_text(html_str: str) -> str:
    ex = _HtmlTextExtractor()
    ex.feed(html_str)
    ex.close()
    return ex.text()


def page_to_text(page: FetchedPage) -> str:
    text = check.isinstance(page.body, bytes).decode('utf-8', 'replace')
    if looks_like_html(text):
        return html_to_text(text)
    return text

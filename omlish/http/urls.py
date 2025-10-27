# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import re
import typing as ta
import urllib.parse

from ..lite.cached import cached_nullary


##


@cached_nullary
def _url_split_host_pat() -> re.Pattern:
    return re.compile('//([^/#?]*)(.*)', re.DOTALL)


def url_split_host(url: str) -> ta.Tuple[ta.Optional[str], str]:
    """splithost('//host[:port]/path') --> 'host[:port]', '/path'."""

    # https://github.com/python/cpython/blob/364ae607d8035db8ba92486ebebd8225446c1a90/Lib/urllib/parse.py#L1143
    if not (m := _url_split_host_pat().match(url)):
        return None, url

    host_port, path = m.groups()
    if path and path[0] != '/':
        path = '/' + path
    return host_port, path


##


def unparse_url_request_path(url: ta.Union[str, urllib.parse.ParseResult]) -> str:
    if isinstance(url, urllib.parse.ParseResult):
        ups = url
    else:
        ups = urllib.parse.urlparse(url)

    return urllib.parse.urlunparse((
        '',
        '',
        ups.path,
        ups.params,
        ups.query,
        ups.fragment,
    ))


def parsed_url_replace(
        url: urllib.parse.ParseResult,
        *,
        scheme: ta.Optional[str] = None,
        netloc: ta.Optional[str] = None,
        path: ta.Optional[str] = None,
        params: ta.Optional[str] = None,
        query: ta.Optional[str] = None,
        fragment: ta.Optional[str] = None,
) -> urllib.parse.ParseResult:
    return urllib.parse.ParseResult(
        scheme if scheme is not None else url.scheme,
        netloc if netloc is not None else url.netloc,
        path if path is not None else url.path,
        params if params is not None else url.params,
        query if query is not None else url.query,
        fragment if fragment is not None else url.fragment,
    )

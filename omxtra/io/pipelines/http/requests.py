# ruff: noqa: UP045
import dataclasses as dc
import typing as ta

from omlish.http.parsing import ParsedHttpMessage
from omlish.http.versions import HttpVersion


##


@dc.dataclass(frozen=True)
class PipelineHttpRequestHead:
    method: str
    target: str
    version: HttpVersion
    headers: dict[str, str]
    parsed: ta.Optional[ParsedHttpMessage] = None

    def header(self, name: str) -> str | None:
        return self.headers.get(name.casefold())


@dc.dataclass(frozen=True)
class FullPipelineHttpRequest:
    head: PipelineHttpRequestHead
    body: bytes


@dc.dataclass(frozen=True)
class PipelineHttpContentChunk:
    data: bytes  # small copy boundary; downstream may hash/update immediately


@dc.dataclass(frozen=True)
class PipelineHttpRequestEnd:
    """Signals end of the current HTTP request body."""


@dc.dataclass(frozen=True)
class PipelineHttpRequestAborted:
    """Signals the peer disconnected before the request body completed."""

    reason: str = 'peer disconnected'

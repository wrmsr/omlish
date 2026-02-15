# ruff: noqa: UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.versions import HttpVersion


##


@dc.dataclass(frozen=True)
class PipelineHttpRequestHead:
    method: str
    target: str
    version: HttpVersion
    headers: HttpHeaders
    parsed: ta.Optional[ParsedHttpMessage] = None


@dc.dataclass(frozen=True)
class FullPipelineHttpRequest:
    head: PipelineHttpRequestHead
    body: bytes


@dc.dataclass(frozen=True)
class PipelineHttpRequestContentChunk:
    data: bytes  # small copy boundary; downstream may hash/update immediately


@dc.dataclass(frozen=True)
class PipelineHttpRequestEnd:
    """Signals end of the current HTTP request body."""


@dc.dataclass(frozen=True)
class PipelineHttpRequestAborted:
    """Signals the peer disconnected before the request body completed."""

    reason: str = 'peer disconnected'

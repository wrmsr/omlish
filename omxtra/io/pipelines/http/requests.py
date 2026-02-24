# ruff: noqa: UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.versions import HttpVersion
from omlish.http.versions import HttpVersions
from omlish.io.streams.types import BytesLikeOrMemoryview


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

    @classmethod
    def simple(
            cls,
            host: str,
            target: str,
            *,
            method: str = 'GET',
            version: HttpVersion = HttpVersions.HTTP_1_1,

            content_type: ta.Optional[str] = None,
            body: bytes = b'',
            connection: str = 'close',

            headers: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> 'FullPipelineHttpRequest':
        return cls(
            head=PipelineHttpRequestHead(
                method=method,
                target=target,
                version=version,
                headers=HttpHeaders([
                    ('Host', host),
                    *([('Content-Type', content_type)] if content_type is not None else []),
                    *([('Content-Length', str(len(body)))] if body else []),
                    ('Connection', connection),
                    *(headers.items() if headers else []),
                ]),
            ),
            body=body,
        )


@dc.dataclass(frozen=True)
class PipelineHttpRequestContentChunkData:
    data: BytesLikeOrMemoryview


@dc.dataclass(frozen=True)
class PipelineHttpRequestEnd:
    """Signals end of the current HTTP request body."""


@dc.dataclass(frozen=True)
class PipelineHttpRequestAborted:
    reason: str

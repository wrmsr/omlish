# ruff: noqa: UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.versions import HttpVersion
from omlish.http.versions import HttpVersions
from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.lite.dataclasses import install_dataclass_kw_only_init

from .objects import FullPipelineHttpMessage
from .objects import PipelineHttpMessageAborted
from .objects import PipelineHttpMessageContentChunkData
from .objects import PipelineHttpMessageEnd
from .objects import PipelineHttpMessageHead
from .objects import PipelineHttpMessageObject
from .objects import PipelineHttpMessageObjects


##


class PipelineHttpRequestObject(PipelineHttpMessageObject, Abstract):
    pass


#


@install_dataclass_kw_only_init()
@dc.dataclass(frozen=True)
class PipelineHttpRequestHead(PipelineHttpMessageHead, PipelineHttpRequestObject):
    method: str
    target: str

    headers: HttpHeaders
    parsed: ta.Optional[ParsedHttpMessage] = None

    version: HttpVersion = HttpVersions.HTTP_1_1


#


@dc.dataclass(frozen=True)
class FullPipelineHttpRequest(FullPipelineHttpMessage, PipelineHttpRequestObject):
    head: PipelineHttpRequestHead
    body: BytesLikeOrMemoryview

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


#


@dc.dataclass(frozen=True)
class PipelineHttpRequestContentChunkData(PipelineHttpMessageContentChunkData, PipelineHttpRequestObject):
    pass


#


@dc.dataclass(frozen=True)
class PipelineHttpRequestEnd(PipelineHttpMessageEnd, PipelineHttpRequestObject):
    pass


#


@dc.dataclass(frozen=True)
class PipelineHttpRequestAborted(PipelineHttpMessageAborted, PipelineHttpRequestObject):
    pass


##


class PipelineHttpRequestObjects(PipelineHttpMessageObjects):
    _head_type: ta.Final = PipelineHttpRequestHead

    def _make_head(self, parsed: ParsedHttpMessage) -> PipelineHttpRequestHead:
        request = check.not_none(parsed.request_line)

        return PipelineHttpRequestHead(
            method=request.method,
            target=check.not_none(request.request_target).decode('utf-8'),
            version=request.http_version,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    #

    _full_type: ta.Final = FullPipelineHttpRequest

    def _make_full(self, head: PipelineHttpMessageHead, body: BytesLikeOrMemoryview) -> FullPipelineHttpRequest:
        return FullPipelineHttpRequest(check.isinstance(head, PipelineHttpRequestHead), body)

    #

    _content_chunk_data_type: ta.Final = PipelineHttpRequestContentChunkData

    def _make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> PipelineHttpRequestContentChunkData:
        return PipelineHttpRequestContentChunkData(data)

    #

    _end_type: ta.Final = PipelineHttpRequestEnd

    def _make_end(self) -> PipelineHttpRequestEnd:
        return PipelineHttpRequestEnd()

    #

    _aborted_type: ta.Final = PipelineHttpRequestAborted

    def _make_aborted(self, reason: ta.Union[str, BaseException]) -> PipelineHttpRequestAborted:
        return PipelineHttpRequestAborted(reason)

# ruff: noqa: UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ...io.streams.types import BytesLike
from ...lite.abstract import Abstract
from ...lite.check import check
from ...lite.dataclasses import install_dataclass_kw_only_init
from ..headers import HttpHeaders
from ..parsing import ParsedHttpMessage
from ..versions import HttpVersion
from ..versions import HttpVersions
from .objects import FullIoPipelineHttpMessage
from .objects import IoPipelineHttpMessageAborted
from .objects import IoPipelineHttpMessageBodyData
from .objects import IoPipelineHttpMessageChunk
from .objects import IoPipelineHttpMessageChunkedTrailers
from .objects import IoPipelineHttpMessageEnd
from .objects import IoPipelineHttpMessageHead
from .objects import IoPipelineHttpMessageLastChunk
from .objects import IoPipelineHttpMessageObject
from .objects import IoPipelineHttpMessageObjects


##


class IoPipelineHttpRequestObject(IoPipelineHttpMessageObject, Abstract):
    pass


#


@install_dataclass_kw_only_init()
@dc.dataclass(frozen=True)
class IoPipelineHttpRequestHead(IoPipelineHttpMessageHead, IoPipelineHttpRequestObject):
    method: str
    target: str

    headers: HttpHeaders
    parsed: ta.Optional[ParsedHttpMessage] = None

    version: HttpVersion = HttpVersions.HTTP_1_1


#


@dc.dataclass(frozen=True)
class FullIoPipelineHttpRequest(FullIoPipelineHttpMessage, IoPipelineHttpRequestObject):
    head: IoPipelineHttpRequestHead
    body: BytesLike

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
    ) -> 'FullIoPipelineHttpRequest':
        return cls(
            head=IoPipelineHttpRequestHead(
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
class IoPipelineHttpRequestChunk(IoPipelineHttpMessageChunk, IoPipelineHttpRequestObject):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpRequestLastChunk(IoPipelineHttpMessageLastChunk, IoPipelineHttpRequestObject):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpRequestChunkedTrailers(IoPipelineHttpMessageChunkedTrailers, IoPipelineHttpRequestObject):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpRequestBodyData(IoPipelineHttpMessageBodyData, IoPipelineHttpRequestObject):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpRequestEnd(IoPipelineHttpMessageEnd, IoPipelineHttpRequestObject):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpRequestAborted(IoPipelineHttpMessageAborted, IoPipelineHttpRequestObject):
    pass


##


class IoPipelineHttpRequestObjects(IoPipelineHttpMessageObjects):
    _head_type: ta.Final = IoPipelineHttpRequestHead

    def _make_head(self, parsed: ParsedHttpMessage) -> IoPipelineHttpRequestHead:
        request = check.not_none(parsed.request_line)

        return IoPipelineHttpRequestHead(
            method=request.method,
            target=check.not_none(request.request_target).decode('utf-8'),
            version=request.http_version,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    #

    _full_type: ta.Final = FullIoPipelineHttpRequest

    def _make_full(self, head: IoPipelineHttpMessageHead, body: BytesLike) -> FullIoPipelineHttpRequest:
        return FullIoPipelineHttpRequest(check.isinstance(head, IoPipelineHttpRequestHead), body)

    #

    _chunk_type: ta.Final = IoPipelineHttpRequestChunk

    def _make_chunk(self, size: int) -> IoPipelineHttpRequestChunk:
        return IoPipelineHttpRequestChunk(size)

    #

    _last_chunk_type: ta.Final = IoPipelineHttpRequestLastChunk

    def _make_last_chunk(self) -> IoPipelineHttpRequestLastChunk:
        return IoPipelineHttpRequestLastChunk()

    #

    _chunked_trailers_type: ta.Final = IoPipelineHttpRequestChunkedTrailers

    def _make_chunked_trailers(self) -> IoPipelineHttpRequestChunkedTrailers:
        return IoPipelineHttpRequestChunkedTrailers()

    #

    _body_data_type: ta.Final = IoPipelineHttpRequestBodyData

    def _make_body_data(self, data: BytesLike) -> IoPipelineHttpRequestBodyData:
        return IoPipelineHttpRequestBodyData(data)

    #

    _end_type: ta.Final = IoPipelineHttpRequestEnd

    def _make_end(self) -> IoPipelineHttpRequestEnd:
        return IoPipelineHttpRequestEnd()

    #

    _aborted_type: ta.Final = IoPipelineHttpRequestAborted

    def _make_aborted(self, reason: ta.Union[str, BaseException]) -> IoPipelineHttpRequestAborted:
        return IoPipelineHttpRequestAborted(reason)

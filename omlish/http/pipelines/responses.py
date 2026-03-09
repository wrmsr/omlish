# ruff: noqa: UP007 UP045
# @omlish-lite
import dataclasses as dc
import http
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
from .objects import IoPipelineHttpMessageEnd
from .objects import IoPipelineHttpMessageHead
from .objects import IoPipelineHttpMessageLastChunk
from .objects import IoPipelineHttpMessageObject
from .objects import IoPipelineHttpMessageObjects
from .objects import IoPipelineHttpMessageChunkedTrailers


##


class IoPipelineHttpResponseObject(IoPipelineHttpMessageObject, Abstract):
    pass


#


@install_dataclass_kw_only_init()
@dc.dataclass(frozen=True)
class IoPipelineHttpResponseHead(IoPipelineHttpMessageHead, IoPipelineHttpResponseObject):
    status: int
    reason: str

    headers: HttpHeaders
    parsed: ta.Optional[ParsedHttpMessage] = None

    version: HttpVersion = HttpVersions.HTTP_1_1

    @staticmethod
    def get_reason_phrase(code: int) -> str:
        try:
            return http.HTTPStatus(code).phrase
        except ValueError:
            return ''


#


@dc.dataclass(frozen=True)
class FullIoPipelineHttpResponse(FullIoPipelineHttpMessage, IoPipelineHttpResponseObject):
    head: IoPipelineHttpResponseHead
    body: BytesLike

    @classmethod
    def simple(
            cls,
            *,
            version: HttpVersion = HttpVersions.HTTP_1_1,
            status: int = 200,
            reason: ta.Optional[str] = None,

            content_type: str = 'text/plain; charset=utf-8',
            body: bytes = b'',
            connection: str = 'close',

            headers: ta.Optional[ta.Mapping[str, str]] = None,
    ):
        return cls(
            head=IoPipelineHttpResponseHead(
                version=version,
                status=status,
                reason=IoPipelineHttpResponseHead.get_reason_phrase(status) if reason is None else reason,
                headers=HttpHeaders([
                    ('Content-Type', content_type),
                    ('Content-Length', str(len(body))),
                    ('Connection', connection),
                    *(headers.items() if headers else []),
                ]),
            ),
            body=body,
        )


#


@dc.dataclass(frozen=True)
class IoPipelineHttpResponseChunk(IoPipelineHttpMessageChunk, IoPipelineHttpResponseObject):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpResponseLastChunk(IoPipelineHttpMessageLastChunk, IoPipelineHttpResponseObject):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpResponseChunkedTrailers(IoPipelineHttpMessageChunkedTrailers, IoPipelineHttpResponseObject):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpResponseBodyData(IoPipelineHttpMessageBodyData, IoPipelineHttpResponseObject):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpResponseEnd(IoPipelineHttpMessageEnd, IoPipelineHttpResponseObject):
    pass


#


@dc.dataclass(frozen=True)
class IoPipelineHttpResponseAborted(IoPipelineHttpMessageAborted, IoPipelineHttpResponseObject):
    pass


##


class IoPipelineHttpResponseObjects(IoPipelineHttpMessageObjects):
    _head_type: ta.Final = IoPipelineHttpResponseHead

    def _make_head(self, parsed: ParsedHttpMessage) -> ta.Any:
        status = check.not_none(parsed.status_line)

        return IoPipelineHttpResponseHead(
            version=status.http_version,
            status=status.status_code,
            reason=status.reason_phrase,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    #

    _full_type: ta.Final = FullIoPipelineHttpResponse

    def _make_full(self, head: IoPipelineHttpMessageHead, body: BytesLike) -> FullIoPipelineHttpResponse:
        return FullIoPipelineHttpResponse(check.isinstance(head, IoPipelineHttpResponseHead), body)

    #

    _chunk_type: ta.Final = IoPipelineHttpResponseChunk

    def _make_chunk(self, size: int) -> IoPipelineHttpResponseChunk:
        return IoPipelineHttpResponseChunk(size)

    #

    _last_chunk_type: ta.Final = IoPipelineHttpResponseLastChunk

    def _make_last_chunk(self) -> IoPipelineHttpResponseLastChunk:
        return IoPipelineHttpResponseLastChunk()

    #

    _chunked_trailers_type: ta.Final = IoPipelineHttpResponseChunkedTrailers

    def _make_chunked_trailers(self) -> IoPipelineHttpResponseChunkedTrailers:
        return IoPipelineHttpResponseChunkedTrailers()

    #

    _body_data_type: ta.Final = IoPipelineHttpResponseBodyData

    def _make_body_data(self, data: BytesLike) -> IoPipelineHttpResponseBodyData:
        return IoPipelineHttpResponseBodyData(data)

    #

    _end_type: ta.Final = IoPipelineHttpResponseEnd

    def _make_end(self) -> IoPipelineHttpResponseEnd:
        return IoPipelineHttpResponseEnd()

    #

    _aborted_type: ta.Final = IoPipelineHttpResponseAborted

    def _make_aborted(self, reason: ta.Union[str, BaseException]) -> IoPipelineHttpResponseAborted:
        return IoPipelineHttpResponseAborted(reason)

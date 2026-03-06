# ruff: noqa: UP045
# @omlish-lite
import dataclasses as dc
import http
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


class PipelineHttpResponseObject(PipelineHttpMessageObject, Abstract):
    pass


#


@install_dataclass_kw_only_init()
@dc.dataclass(frozen=True)
class PipelineHttpResponseHead(PipelineHttpMessageHead, PipelineHttpResponseObject):
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
class FullPipelineHttpResponse(FullPipelineHttpMessage, PipelineHttpResponseObject):
    head: PipelineHttpResponseHead
    body: BytesLikeOrMemoryview

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
            head=PipelineHttpResponseHead(
                version=version,
                status=status,
                reason=PipelineHttpResponseHead.get_reason_phrase(status) if reason is None else reason,
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
class PipelineHttpResponseContentChunkData(PipelineHttpMessageContentChunkData, PipelineHttpResponseObject):
    pass


#


@dc.dataclass(frozen=True)
class PipelineHttpResponseEnd(PipelineHttpMessageEnd, PipelineHttpResponseObject):
    pass


#


@dc.dataclass(frozen=True)
class PipelineHttpResponseAborted(PipelineHttpMessageAborted, PipelineHttpResponseObject):
    pass


##


class PipelineHttpResponseObjects(PipelineHttpMessageObjects):
    _head_type: ta.Final[ta.Type[PipelineHttpResponseHead]] = PipelineHttpResponseHead

    def _make_head(self, parsed: ParsedHttpMessage) -> ta.Any:
        status = check.not_none(parsed.status_line)

        return PipelineHttpResponseHead(
            version=status.http_version,
            status=status.status_code,
            reason=status.reason_phrase,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    #

    _full_type: ta.Final[ta.Type[FullPipelineHttpResponse]] = FullPipelineHttpResponse

    def _make_full(self, head: PipelineHttpMessageHead, body: BytesLikeOrMemoryview) -> FullPipelineHttpResponse:
        return FullPipelineHttpResponse(check.isinstance(head, PipelineHttpResponseHead), body)

    #

    _content_chunk_data_type: ta.Final[ta.Type[PipelineHttpResponseContentChunkData]] = PipelineHttpResponseContentChunkData  # noqa

    def _make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> PipelineHttpResponseContentChunkData:
        return PipelineHttpResponseContentChunkData(data)

    #

    _end_type: ta.Final[ta.Type[PipelineHttpResponseEnd]] = PipelineHttpResponseEnd

    def _make_end(self) -> PipelineHttpResponseEnd:
        return PipelineHttpResponseEnd()

    #

    _aborted_type: ta.Final[ta.Type[PipelineHttpResponseAborted]] = PipelineHttpResponseAborted

    def _make_aborted(self, reason: ta.Union[str, BaseException]) -> PipelineHttpResponseAborted:
        return PipelineHttpResponseAborted(reason)

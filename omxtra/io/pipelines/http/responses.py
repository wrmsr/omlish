# ruff: noqa: UP045
# @omlish-lite
import dataclasses as dc
import http
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.versions import HttpVersion
from omlish.http.versions import HttpVersions
from omlish.lite.abstract import Abstract
from omlish.lite.dataclasses import install_dataclass_kw_only_init

from .objects import FullPipelineHttpMessage
from .objects import PipelineHttpMessageAborted
from .objects import PipelineHttpMessageContentChunkData
from .objects import PipelineHttpMessageEnd
from .objects import PipelineHttpMessageHead
from .objects import PipelineHttpMessageObject


##


class PipelineHttpResponseObject(PipelineHttpMessageObject, Abstract):
    pass


@install_dataclass_kw_only_init()
@dc.dataclass(frozen=True)
class PipelineHttpResponseHead(PipelineHttpMessageHead, PipelineHttpResponseObject):
    status: int
    reason: str

    version: HttpVersion
    headers: HttpHeaders
    parsed: ta.Optional[ParsedHttpMessage] = None


@dc.dataclass(frozen=True)
class FullPipelineHttpResponse(FullPipelineHttpMessage, PipelineHttpResponseObject):
    head: PipelineHttpResponseHead
    body: bytes

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
                reason=cls._get_reason_phrase(status) if reason is None else reason,
                headers=HttpHeaders([
                    ('Content-Type', content_type),
                    ('Content-Length', str(len(body))),
                    ('Connection', connection),
                    *(headers.items() if headers else []),
                ]),
            ),
            body=body,
        )

    @staticmethod
    def _get_reason_phrase(code: int) -> str:
        try:
            return http.HTTPStatus(code).phrase
        except ValueError:
            return ''


@dc.dataclass(frozen=True)
class PipelineHttpResponseContentChunkData(PipelineHttpMessageContentChunkData, PipelineHttpResponseObject):
    pass


@dc.dataclass(frozen=True)
class PipelineHttpResponseEnd(PipelineHttpMessageEnd, PipelineHttpResponseObject):
    pass


@dc.dataclass(frozen=True)
class PipelineHttpResponseAborted(PipelineHttpMessageAborted, PipelineHttpResponseObject):
    pass

# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.http.headers import HttpHeaders


##


@dc.dataclass()
class PipelineHttpTransferEncodingError(Exception):
    reason: str


@ta.final
@dc.dataclass(frozen=True)
class PipelineHttpTransferEncoding:
    mode: ta.Literal['none', 'eof', 'cl', 'chunked']
    length: ta.Optional[int]

    @classmethod
    def select(
            cls,
            headers: HttpHeaders,
            *,
            if_length_missing: ta.Literal['none', 'eof'],
    ) -> 'PipelineHttpTransferEncoding':
        if headers.contains_value('transfer-encoding', 'chunked', ignore_case=True):
            return cls('chunked', None)

        cl = headers.single.get('content-length')
        if not cl:
            return cls(if_length_missing, None)

        try:
            n = int(cl)
        except ValueError:
            raise PipelineHttpTransferEncodingError('bad Content-Length') from None

        if n < 0:
            raise PipelineHttpTransferEncodingError('bad Content-Length')

        if n == 0:
            return cls('none', None)

        return cls('cl', n)

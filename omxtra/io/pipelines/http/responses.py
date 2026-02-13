# ruff: noqa: UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.versions import HttpVersion


##


@dc.dataclass(frozen=True)
class PipelineHttpResponseHead:
    version: HttpVersion
    status: int
    reason: str
    headers: HttpHeaders
    parsed: ta.Optional[ParsedHttpMessage] = None

import typing as ta

from ... import dataclasses as dc
from ..statuses import HttpStatus
from ._compat import compat


ResponseData: ta.TypeAlias = str | ta.Iterable[str] | bytes | ta.Iterable[bytes]
ResponseStatus: ta.TypeAlias = int | str | HttpStatus
ResponseHeaders: ta.TypeAlias = ta.Mapping[str, str | ta.Iterable[str]] | ta.Iterable[tuple[str, str]]


##


@compat
@dc.dataclass(frozen=True)
class Response:
    response: ResponseData | None = None
    status: ResponseStatus | None = None
    headers: ResponseHeaders | None = None
    mimetype: str | None = None
    content_type: str | None = None

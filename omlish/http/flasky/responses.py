from ... import dataclasses as dc
from ._compat import compat


##


@compat
@dc.dataclass(frozen=True, kw_only=True)
class Response:
    data: str | None = None

import typing as ta

from ... import dataclasses as dc
from ._compat import compat
from .types import ImmutableMultiDict


##


@compat
@dc.dataclass(frozen=True, kw_only=True)
class Request:
    path: str
    method: str

    form: ImmutableMultiDict[str, str] | None = None

    def get_json(self) -> ta.Any:
        raise NotImplementedError

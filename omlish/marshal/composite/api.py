import dataclasses as dc
import typing as ta

from ..api.options import Option


##


@dc.dataclass(frozen=True, kw_only=True)
class DefaultIterableConstructors(Option):
    iterable: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None
    sequence: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None
    mutable_sequence: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None

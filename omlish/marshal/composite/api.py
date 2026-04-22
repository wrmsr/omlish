import dataclasses as dc
import typing as ta

from ... import typedvalues as tv
from ..api.options import Option


##


@dc.dataclass(frozen=True, kw_only=True)
class DefaultIterableConstructors(Option, tv.UniqueTypedValue):
    iterable: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None
    sequence: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None
    mutable_sequence: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None


@dc.dataclass(frozen=True, kw_only=True)
class DefaultMappingConstructors(Option, tv.UniqueTypedValue):
    mapping: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None
    mutable_mapping: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None

"""
TODO:
 - individual options?
"""
import collections.abc
import dataclasses as dc
import typing as ta

from ... import lang
from ... import typedvalues as tv
from ..api.options import Option


##


DEFAULT_ITERABLE_CONCRETE_TYPES: ta.Final[ta.Mapping[type[collections.abc.Iterable], type[collections.abc.Iterable]]] = {  # noqa
    collections.abc.Iterable: tuple,  # type: ignore
    collections.abc.Sequence: tuple,  # type: ignore
    collections.abc.MutableSequence: list,  # type: ignore
}


@dc.dataclass(frozen=True, kw_only=True)
class DefaultIterableConstructors(Option, tv.UniqueTypedValue, lang.Final):
    iterable: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None
    sequence: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None
    mutable_sequence: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None


##


DEFAULT_MAPPING_CONCRETE_TYPES: ta.Final[ta.Mapping[type[collections.abc.Mapping], type[collections.abc.Mapping]]] = {
    collections.abc.Mapping: dict,  # type: ignore
    collections.abc.MutableMapping: dict,  # type: ignore
}


@dc.dataclass(frozen=True, kw_only=True)
class DefaultMappingConstructors(Option, tv.UniqueTypedValue, lang.Final):
    mapping: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None
    mutable_mapping: ta.Callable[[ta.Iterable], ta.Any] | ta.Any | None = None

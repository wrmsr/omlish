import typing as ta

from ... import cached
from ... import collections as col
from ... import dataclasses as dc
from .types import DEFAULT_FIELD_OPTIONS
from .types import FieldOptions


##


@dc.dataclass(frozen=True, kw_only=True)
class FieldInfo:
    """
    Computed field information - derived from FieldMetadata + dataclass introspection.

    This is purely derived/computed data, not configuration. The metadata field contains the final merged configuration.
    """

    name: str
    type: ta.Any

    marshal_name: str | None
    unmarshal_names: ta.Sequence[str]

    options: FieldOptions = DEFAULT_FIELD_OPTIONS


@dc.dataclass(frozen=True)
class FieldInfos:
    """Collection of field infos with convenient lookups."""

    lst: ta.Sequence[FieldInfo]

    def __iter__(self) -> ta.Iterator[FieldInfo]:
        return iter(self.lst)

    def __len__(self) -> int:
        return len(self.lst)

    @cached.property
    @dc.init
    def by_name(self) -> ta.Mapping[str, FieldInfo]:
        return col.make_map(((fi.name, fi) for fi in self), strict=True)

    @cached.property
    @dc.init
    def by_marshal_name(self) -> ta.Mapping[str, FieldInfo]:
        return col.make_map(((fi.marshal_name, fi) for fi in self if fi.marshal_name is not None), strict=True)

    @cached.property
    @dc.init
    def by_unmarshal_name(self) -> ta.Mapping[str, FieldInfo]:
        return col.make_map(((n, fi) for fi in self for n in fi.unmarshal_names), strict=True)

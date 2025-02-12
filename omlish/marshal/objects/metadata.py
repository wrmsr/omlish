import typing as ta

from ... import cached
from ... import collections as col
from ... import dataclasses as dc
from ... import lang
from ..base import Marshaler
from ..base import MarshalerFactory
from ..base import Unmarshaler
from ..base import UnmarshalerFactory
from ..naming import Naming


##


@dc.dataclass(frozen=True, kw_only=True)
class FieldOptions:
    omit_if: ta.Callable[[ta.Any], bool] | None = None

    default: lang.Maybe[ta.Any] = dc.xfield(default=lang.empty(), check_type=lang.Maybe)

    embed: bool = False

    no_marshal: bool = False
    no_unmarshal: bool = False


DEFAULT_FIELD_OPTIONS = FieldOptions()
FIELD_OPTIONS_KWARGS: frozenset[str] = frozenset(dc.fields_dict(FieldOptions).keys())


@dc.dataclass(frozen=True, kw_only=True)
class FieldMetadata:
    name: str | None = None
    alts: ta.Iterable[str] | None = None

    options: FieldOptions = DEFAULT_FIELD_OPTIONS

    marshaler: Marshaler | None = dc.xfield(None, check_type=(Marshaler, None))
    marshaler_factory: MarshalerFactory | None = None

    unmarshaler: Unmarshaler | None = dc.xfield(None, check_type=(Unmarshaler, None))
    unmarshaler_factory: UnmarshalerFactory | None = None

    def update(self, **kwargs: ta.Any) -> 'FieldMetadata':
        okw = {k: v for k, v in kwargs.items() if k in FIELD_OPTIONS_KWARGS}
        mkw = {k: v for k, v in kwargs.items() if k not in FIELD_OPTIONS_KWARGS}
        return dc.replace(
            self,
            **(dict(options=dc.replace(self.options, **okw)) if okw else {}),
            **mkw,
        )


@dc.dataclass(frozen=True, kw_only=True)
class ObjectMetadata:
    field_naming: Naming | None = None

    unknown_field: str | None = None
    source_field: str | None = None

    @cached.property
    def specials(self) -> 'ObjectSpecials':
        return ObjectSpecials(
            unknown=self.unknown_field,
            source=self.source_field,
        )

    field_defaults: FieldMetadata = FieldMetadata()

    ignore_unknown: bool = False


@dc.dataclass(frozen=True, kw_only=True)
class ObjectSpecials:
    unknown: str | None = None
    source: str | None = None

    @cached.property
    def set(self) -> frozenset[str]:
        return frozenset(v for v in dc.asdict(self).values() if v is not None)


##


@dc.dataclass(frozen=True, kw_only=True)
class FieldInfo:
    name: str
    type: ta.Any

    marshal_name: str | None
    unmarshal_names: ta.Sequence[str]

    metadata: FieldMetadata = FieldMetadata()

    options: FieldOptions = FieldOptions()


@dc.dataclass(frozen=True)
class FieldInfos:
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

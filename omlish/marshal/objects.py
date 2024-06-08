"""
TODO:
 - cfg naming
 - adapters for dataclasses / namedtuples / user objects (as confitured)
"""
import collections.abc
import enum
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import Option
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .values import Value


##


class FieldNaming(Option, enum.Enum):
    SNAKE = 'snake'
    CAMEL = 'camel'


@dc.dataclass(frozen=True)
class ObjectMetadata:
    field_naming: FieldNaming | None = None

    unknown_field: str | None = None


@dc.dataclass(frozen=True)
class FieldMetadata:
    name: str | None = None
    alts: ta.Iterable[str] | None = None

    marshaler: Marshaler | None = None
    marshaler_factory: MarshalerFactory | None = None

    unmarshaler: Unmarshaler | None = None
    unmarshaler_factory: UnmarshalerFactory | None = None


##


@dc.dataclass(frozen=True)
class FieldInfo:
    name: str
    type: ta.Any
    metadata: FieldMetadata

    marshal_name: str
    unmarshal_names: ta.Sequence[str]


def name_field(n: str, e: FieldNaming) -> str:
    if e is FieldNaming.SNAKE:
        return lang.snake_case(n)
    if e is FieldNaming.CAMEL:
        return lang.camel_case(n)
    raise ValueError(e)


##


@dc.dataclass(frozen=True)
class ObjectMarshaler(Marshaler):
    fields: ta.Sequence[tuple[FieldInfo, Marshaler]]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return {
            fi.marshal_name: m.marshal(ctx, getattr(o, fi.name))
            for fi, m in self.fields
        }


##


@dc.dataclass(frozen=True)
class ObjectUnmarshaler(Unmarshaler):
    cls: type
    fields_by_unmarshal_name: ta.Mapping[str, tuple[FieldInfo, Unmarshaler]]
    unknown_field: str | None = None

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        ma = check.isinstance(v, collections.abc.Mapping)
        u: ta.Any
        u = {} if self.unknown_field is not None else None
        kw = {}
        for k, mv in ma.items():
            try:
                fi, u = self.fields_by_unmarshal_name[k]  # type: ignore
            except KeyError:
                # FIXME:
                # if u is not None:
                #     u[k] =
                continue
            if fi.name in kw:
                raise KeyError(f'Duplicate keys for field {fi.name!r}: {k!r}')
            kw[fi.name] = u.unmarshal(ctx, mv)
        return self.cls(**kw)

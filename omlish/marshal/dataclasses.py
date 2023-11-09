"""
TODO:
 - cfg naming
"""
import collections.abc
import dataclasses as dc
import typing as ta

from .. import check
from .. import collections as col
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import Option
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .values import Value


##


@dc.dataclass(frozen=True)
class Field:
    name: str | None = None
    alts: ta.Iterable[str] | None = None

    marshaler: Marshaler | None = None
    marshaler_factory: MarshalerFactory | None = None

    unmarshaler: Unmarshaler | None = None
    unmarshaler_factory: UnmarshalerFactory | None = None


@dc.dataclass(frozen=True)
class FieldInfo:
    field: dc.Field
    type: ta.Any
    metadata: Field | None

    marshal_name: str

    unmarshal_name: str
    unmarshal_alts: ta.AbstractSet[str]


def get_field_infos(ty: type, opts: col.TypeMap[Option] = col.TypeMap()) -> ta.Sequence[FieldInfo]:
    type_hints = ta.get_type_hints(ty)

    ret: list[FieldInfo] = []
    for field in dc.fields(ty):
        kw = dict(
            field=field,
            type=type_hints[field.name],
            metadata=None,

            marshal_name=field.name,

            unmarshal_name=field.name,
            unmarshal_alts=frozenset(),
        )

        if (metadata := field.metadata.get(Field)) is not None:
            kw.update(metadata=metadata)

            if metadata.name is not None:
                kw.update(
                    marshal_name=metadata.name,

                    unmarshal_name=metadata.name,
                    unmarshal_alts=frozenset(metadata.alts or ()),
                )

        ret.append(FieldInfo(**kw))

    return ret


##


@dc.dataclass(frozen=True)
class DataclassMarshaler(Marshaler):
    fields: ta.Sequence[tuple[FieldInfo, Marshaler]]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return {
            fi.marshal_name: m.marshal(ctx, getattr(o, fi.field.name))
            for fi, m in self.fields
        }


class DataclassMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, rty: rfl.Type) -> ta.Optional[Marshaler]:
        if isinstance(rty, type) and dc.is_dataclass(rty):
            fields = [
                (fi, ctx.make(fi.type))
                for fi in get_field_infos(rty, ctx.options)
            ]
            return DataclassMarshaler(fields)
        return None


##


@dc.dataclass(frozen=True)
class DataclassUnmarshaler(Unmarshaler):
    cls: type
    fields: ta.Sequence[tuple[FieldInfo, Unmarshaler]]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        ma = check.isinstance(v, collections.abc.Mapping)
        return self.cls(**{  # type: ignore
            fi.field.name: u.unmarshal(ctx, ma[fi.unmarshal_name])
            for fi, u in self.fields
        })


class DataclassUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, rty: rfl.Type) -> ta.Optional[Unmarshaler]:
        if isinstance(rty, type) and dc.is_dataclass(rty):
            fields = [
                (fi, ctx.make(fi.type))
                for fi in get_field_infos(rty, ctx.options)
            ]
            return DataclassUnmarshaler(rty, fields)
        return None

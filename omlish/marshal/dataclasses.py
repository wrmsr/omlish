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
    metadata: Field

    marshal_name: str
    unmarshal_names: ta.Sequence[str]


def get_field_infos(ty: type, opts: col.TypeMap[Option] = col.TypeMap()) -> ta.Sequence[FieldInfo]:
    type_hints = ta.get_type_hints(ty)

    ret: list[FieldInfo] = []
    for field in dc.fields(ty):
        kw = dict(
            field=field,
            type=type_hints[field.name],
            metadata=Field(),

            marshal_name=field.name,
            unmarshal_names=[field.name],
        )

        if (metadata := field.metadata.get(Field)) is not None:
            kw.update(metadata=metadata)

            if metadata.name is not None:
                kw.update(
                    marshal_name=metadata.name,
                    unmarshal_names=col.unique([metadata.name, *(metadata.alts or ())]),
                )

        ret.append(FieldInfo(**kw))

    return ret


def _make_field_obj(ctx, ty, obj, fac):
    if obj is not None:
        return obj
    if fac is not None:
        return fac(ctx, ty)
    return ctx.make(ty)


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
                (fi, _make_field_obj(ctx, fi.type, fi.metadata.marshaler, fi.metadata.marshaler_factory))
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

        kw = {}
        for fi, u in self.fields:
            mv: Value = None
            seen = None
            for un in fi.unmarshal_names:
                try:
                    cv = ma[un]  # type: ignore
                except KeyError:
                    continue
                if seen:
                    raise KeyError(f'Duplicate keys for field {fi.field.name!r}: {seen!r}, {un!r}')
                mv = cv  # type: ignore
                seen = un

            if seen:
                kw[fi.field.name] = u.unmarshal(ctx, mv)

        return self.cls(**kw)


class DataclassUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, rty: rfl.Type) -> ta.Optional[Unmarshaler]:
        if isinstance(rty, type) and dc.is_dataclass(rty):
            fields = [
                (fi, _make_field_obj(ctx, fi.type, fi.metadata.unmarshaler, fi.metadata.unmarshaler_factory))
                for fi in get_field_infos(rty, ctx.options)
            ]
            return DataclassUnmarshaler(rty, fields)
        return None

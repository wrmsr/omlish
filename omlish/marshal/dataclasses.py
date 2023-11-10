"""
TODO:
 - cfg naming
"""
import collections.abc
import enum
import typing as ta

from .. import cached
from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import lang
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


class FieldNaming(Option, enum.Enum):
    SNAKE = 'snake'
    CAMEL = 'camel'


@dc.dataclass(frozen=True)
class DataclassMetadata:
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
    field: dc.Field
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


def get_dataclass_metadata(ty: type) -> DataclassMetadata:
    return check.optional_single(
        e
        for e in dc.get_merged_metadata(ty).get(dc.UserMetadata, [])
        if isinstance(e, DataclassMetadata)
    ) or DataclassMetadata()


def get_field_infos(ty: type, opts: col.TypeMap[Option] = col.TypeMap()) -> ta.Sequence[FieldInfo]:
    dc_md = get_dataclass_metadata(ty)
    dc_naming = dc_md.field_naming or opts.get(FieldNaming)

    type_hints = ta.get_type_hints(ty)

    ret: list[FieldInfo] = []
    for field in dc.fields(ty):
        if (f_naming := field.metadata.get(FieldNaming, dc_naming)) is not None:
            um_name = name_field(field.name, f_naming)
        else:
            um_name = field.name

        kw = dict(
            field=field,
            type=type_hints[field.name],
            metadata=FieldMetadata(),

            marshal_name=um_name,
            unmarshal_names=[um_name],
        )

        if (fmd := field.metadata.get(FieldMetadata)) is not None:
            kw.update(metadata=fmd)

            if fmd.name is not None:
                kw.update(
                    marshal_name=fmd.name,
                    unmarshal_names=col.unique([fmd.name, *(fmd.alts or ())]),
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
    fields_by_unmarshal_name: ta.Mapping[str, tuple[FieldInfo, Unmarshaler]]
    unknown_field: str | None = None

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        ma = check.isinstance(v, collections.abc.Mapping)
        u = {} if self.unknown_field is not None else None
        kw = {}
        for k, mv in ma.items():
            try:
                fi, u = self.fields_by_unmarshal_name[k]
            except KeyError:
                # FIXME:
                # if u is not None:
                #     u[k] =
                continue
            if fi.field.name in kw:
                raise KeyError(f'Duplicate keys for field {fi.field.name!r}: {k!r}')
            kw[fi.field.name] = u.unmarshal(ctx, mv)
        return self.cls(**kw)


class DataclassUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, rty: rfl.Type) -> ta.Optional[Unmarshaler]:
        if isinstance(rty, type) and dc.is_dataclass(rty):
            dc_md = get_dataclass_metadata(rty)
            d: dict[str, tuple[FieldInfo, Unmarshaler]] = {}
            for fi in get_field_infos(rty, ctx.options):
                tup = (fi, _make_field_obj(ctx, fi.type, fi.metadata.unmarshaler, fi.metadata.unmarshaler_factory))
                for un in fi.unmarshal_names:
                    if un in d:
                        raise KeyError(f'Duplicate fields for name {un!r}: {fi.field.name!r}, {d[un][0].field.name!r}')
                    d[un] = tup
            return DataclassUnmarshaler(rty, d)
        return None

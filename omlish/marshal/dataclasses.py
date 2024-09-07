import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import Option
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .naming import Naming
from .naming import translate_name
from .objects import FieldInfo
from .objects import FieldMetadata
from .objects import ObjectMarshaler
from .objects import ObjectMetadata
from .objects import ObjectUnmarshaler


##


def get_dataclass_metadata(ty: type) -> ObjectMetadata:
    return check.optional_single(
        e
        for e in dc.get_merged_metadata(ty).get(dc.UserMetadata, [])
        if isinstance(e, ObjectMetadata)
    ) or ObjectMetadata()


def get_field_infos(
        ty: type,
        opts: col.TypeMap[Option] = col.TypeMap(),
) -> ta.Sequence[FieldInfo]:
    dc_md = get_dataclass_metadata(ty)
    dc_naming = dc_md.field_naming or opts.get(Naming)

    fi_defaults = {
        k: v
        for k, v in dc.asdict(dc_md.field_defaults).items()
        if v is not None
    }

    type_hints = ta.get_type_hints(ty)

    ret: list[FieldInfo] = []
    for field in dc.fields(ty):
        if (f_naming := field.metadata.get(Naming, dc_naming)) is not None:
            um_name = translate_name(field.name, f_naming)
        else:
            um_name = field.name

        kw = dict(fi_defaults)
        kw.update(
            name=field.name,
            type=type_hints[field.name],
            metadata=FieldMetadata(),

            marshal_name=um_name,
            unmarshal_names=[um_name],
        )

        if (fmd := field.metadata.get(FieldMetadata)) is not None:
            kw.update(
                metadata=fmd,
                omit_if=fmd.omit_if,
            )

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


class DataclassMarshalerFactory(MarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and dc.is_dataclass(rty)

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        ty = check.isinstance(rty, type)
        check.state(dc.is_dataclass(ty))
        dc_md = get_dataclass_metadata(ty)
        fields = [
            (fi, _make_field_obj(ctx, fi.type, fi.metadata.marshaler, fi.metadata.marshaler_factory))
            for fi in get_field_infos(ty, ctx.options)
        ]
        return ObjectMarshaler(
            fields,
            unknown_field=dc_md.unknown_field,
        )


##


class DataclassUnmarshalerFactory(UnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and dc.is_dataclass(rty)

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        ty = check.isinstance(rty, type)
        check.state(dc.is_dataclass(ty))
        dc_md = get_dataclass_metadata(ty)
        d: dict[str, tuple[FieldInfo, Unmarshaler]] = {}
        for fi in get_field_infos(ty, ctx.options):
            tup = (fi, _make_field_obj(ctx, fi.type, fi.metadata.unmarshaler, fi.metadata.unmarshaler_factory))
            for un in fi.unmarshal_names:
                if un in d:
                    raise KeyError(f'Duplicate fields for name {un!r}: {fi.name!r}, {d[un][0].name!r}')
                d[un] = tup
        return ObjectUnmarshaler(
            ty,
            d,
            unknown_field=dc_md.unknown_field,
        )

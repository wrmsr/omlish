"""
TODO:
 - tangled with objects - Field/ObjectMetadata defined over there but unused
"""
import typing as ta

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
from .naming import Naming
from .naming import translate_name
from .objects import DEFAULT_FIELD_OPTIONS
from .objects import FIELD_OPTIONS_KWARGS
from .objects import FieldInfo
from .objects import FieldInfos
from .objects import FieldMetadata
from .objects import FieldOptions
from .objects import ObjectMarshaler
from .objects import ObjectMetadata
from .objects import ObjectUnmarshaler


##


def get_dataclass_metadata(ty: type) -> ObjectMetadata:
    return check.opt_single(
        e
        for e in dc.get_merged_metadata(ty).get(dc.UserMetadata, [])
        if isinstance(e, ObjectMetadata)
    ) or ObjectMetadata()


def get_field_infos(
        ty: type,
        opts: col.TypeMap[Option] = col.TypeMap(),
) -> FieldInfos:
    dc_md = get_dataclass_metadata(ty)
    dc_naming = dc_md.field_naming or opts.get(Naming)

    fi_defaults = {
        k: v
        for k, v in dc.asdict(dc_md.field_defaults).items()
        if v is not None
    }
    fo_defaults = {
        k: v
        for k, v in fi_defaults.pop('options').items()
        if v != getattr(DEFAULT_FIELD_OPTIONS, k)
    }

    type_hints = ta.get_type_hints(ty)

    ret: list[FieldInfo] = []
    for field in dc.fields(ty):
        if (f_naming := field.metadata.get(Naming, dc_naming)) is not None:
            um_name = translate_name(field.name, f_naming)
        else:
            um_name = field.name

        fi_kw = dict(fi_defaults)
        fo_kw = dict(fo_defaults)

        fi_kw.update(
            name=field.name,
            type=type_hints[field.name],
            metadata=FieldMetadata(),

            marshal_name=um_name,
            unmarshal_names=[um_name],
        )

        has_set_name = False
        if (fmd := field.metadata.get(FieldMetadata)) is not None:
            fi_kw.update(
                metadata=fmd,
            )

            for fo_k in FIELD_OPTIONS_KWARGS:
                if (fo_v := getattr(fmd.options, fo_k)) != getattr(DEFAULT_FIELD_OPTIONS, fo_k):
                    fo_kw[fo_k] = fo_v

            if fmd.name is not None:
                has_set_name = True
                fi_kw.update(
                    marshal_name=fmd.name,
                    unmarshal_names=col.unique([fmd.name, *(fmd.alts or ())]),
                )

        if fo_kw.get('embed') and not has_set_name:
            fi_kw.update(
                marshal_name=fi_kw['marshal_name'] + '_',
                unmarshal_names=[n + '_' for n in fi_kw['unmarshal_names']],
            )

        if fo_kw.get('no_marshal'):
            fi_kw.update(
                marshal_name=None,
            )
        if fo_kw.get('no_unmarshal'):
            fi_kw.update(
                unmarshal_names=(),
            )

        ret.append(
            FieldInfo(
                options=FieldOptions(**fo_kw),
                **fi_kw,
            ),
        )

    return FieldInfos(ret)


def _make_field_obj(ctx, ty, obj, fac):
    if obj is not None:
        return obj
    if fac is not None:
        return fac(ctx, ty)
    return ctx.make(ty)


##


class DataclassMarshalerFactory(MarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and dc.is_dataclass(rty) and not lang.is_abstract_class(rty)

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        ty = check.isinstance(rty, type)
        check.state(dc.is_dataclass(ty))
        check.state(not lang.is_abstract_class(ty))

        dc_md = get_dataclass_metadata(ty)
        fis = get_field_infos(ty, ctx.options)

        fields = [
            (fi, _make_field_obj(ctx, fi.type, fi.metadata.marshaler, fi.metadata.marshaler_factory))
            for fi in fis
            if fi.name not in dc_md.specials.set
        ]

        return ObjectMarshaler(
            fields,
            specials=dc_md.specials,
        )


##


class DataclassUnmarshalerFactory(UnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and dc.is_dataclass(rty) and not lang.is_abstract_class(rty)

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        ty = check.isinstance(rty, type)
        check.state(dc.is_dataclass(ty))
        check.state(not lang.is_abstract_class(ty))

        dc_md = get_dataclass_metadata(ty)
        fis = get_field_infos(ty, ctx.options)

        d: dict[str, tuple[FieldInfo, Unmarshaler]] = {}
        defaults: dict[str, ta.Any] = {}
        embeds: dict[str, type] = {}
        embeds_by_unmarshal_name: dict[str, tuple[str, str]] = {}

        def add_field(fi: FieldInfo, *, prefixes: ta.Iterable[str] = ('',)) -> ta.Iterable[str]:
            ret: list[str] = []

            if fi.options.embed:
                e_ty = check.isinstance(fi.type, type)
                check.state(dc.is_dataclass(e_ty))
                e_dc_md = get_dataclass_metadata(e_ty)
                if e_dc_md.specials.set:
                    raise Exception(f'Embedded fields cannot have specials: {e_ty}')

                embeds[fi.name] = e_ty
                for e_fi in get_field_infos(e_ty, ctx.options):
                    e_ns = add_field(e_fi, prefixes=[p + ep for p in prefixes for ep in fi.unmarshal_names])
                    embeds_by_unmarshal_name.update({e_f: (fi.name, e_fi.name) for e_f in e_ns})
                    ret.extend(e_ns)

            else:
                tup = (fi, _make_field_obj(ctx, fi.type, fi.metadata.unmarshaler, fi.metadata.unmarshaler_factory))

                for pfx in prefixes:
                    for un in fi.unmarshal_names:
                        un = pfx + un
                        if un in d:
                            raise KeyError(f'Duplicate fields for name {un!r}: {fi.name!r}, {d[un][0].name!r}')
                        d[un] = tup
                        ret.append(un)

                if fi.options.default.present:
                    defaults[fi.name] = fi.options.default.must()

            return ret

        for fi in fis:
            if fi.name in dc_md.specials.set:
                continue
            add_field(fi)

        return ObjectUnmarshaler(
            ty,
            d,
            specials=dc_md.specials,
            defaults=defaults,
            embeds=embeds,
            embeds_by_unmarshal_name=embeds_by_unmarshal_name,
            ignore_unknown=dc_md.ignore_unknown,
        )

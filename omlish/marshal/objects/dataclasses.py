"""
TODO:
 - clean up yeesh
 - tangled with objects - Field/ObjectMetadata defined over there but unused
"""
import typing as ta

from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ...lite import marshal as lm
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.errors import UnhandledTypeError
from ..base.options import Option
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from ..naming import Naming
from ..naming import translate_name
from .marshal import ObjectMarshaler
from .metadata import DEFAULT_FIELD_OPTIONS
from .metadata import FIELD_OPTIONS_KWARGS
from .metadata import FieldInfo
from .metadata import FieldInfos
from .metadata import FieldMetadata
from .metadata import FieldOptions
from .metadata import ObjectMetadata
from .unmarshal import ObjectUnmarshaler


##


def get_dataclass_metadata(ty: type) -> ObjectMetadata:
    return check.single(dc.reflect(ty).spec.metadata_by_type.get(ObjectMetadata) or [ObjectMetadata()])


def get_dataclass_field_infos(
        ty: type,
        opts: col.TypeMap[Option] | None = None,
) -> FieldInfos:
    if opts is None:
        opts = col.TypeMap()

    dc_md = get_dataclass_metadata(ty)
    dc_naming = dc_md.field_naming or opts.get(Naming)
    dc_rfl = dc.reflect(ty)

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
    for field in dc_rfl.instance_fields:
        if (f_naming := field.metadata.get(Naming, dc_naming)) is not None:
            um_name = translate_name(field.name, f_naming)
        else:
            um_name = field.name

        fmd: FieldMetadata | None = field.metadata.get(FieldMetadata)

        f_ty: ta.Any
        if (
                dc_rfl.spec.generic_init or
                (fmd is not None and fmd.options.generic_replace)
        ):
            f_ty = rfl.to_annotation(dc_rfl.fields_inspection.generic_replaced_field_type(field.name))
        else:
            f_ty = type_hints[field.name]

        fi_kw = dict(fi_defaults)
        fo_kw = dict(fo_defaults)

        fi_kw.update(
            name=field.name,
            type=f_ty,
            metadata=FieldMetadata(),

            marshal_name=um_name,
            unmarshal_names=[um_name],
        )

        has_set_name = False
        if fmd is not None:
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

        else:
            try:
                lfk = field.metadata[lm.OBJ_MARSHALER_FIELD_KEY]
            except KeyError:
                pass
            else:
                if lfk is not None:
                    check.non_empty_str(lfk)
                    has_set_name = True
                    fi_kw.update(
                        marshal_name=lfk,
                        unmarshal_names=[lfk],
                    )
                else:
                    fo_kw.update(
                        no_marshal=True,
                        no_unmarshal=True,
                    )

            if (lon := field.metadata.get(lm.OBJ_MARSHALER_OMIT_IF_NONE)) is not None:
                if check.isinstance(lon, bool):
                    fo_kw.update(
                        omit_if=lang.is_none,
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


##


def _make_field_marshal_obj(
        ctx: MarshalFactoryContext,
        ty: ta.Any,
        obj: Marshaler | None,
        fac: MarshalerFactory | None,
):
    if obj is not None:
        return obj
    if fac is not None:
        if (m := fac.make_marshaler(ctx, ty)) is None:
            raise UnhandledTypeError(ty)
        return m()
    return ctx.make_marshaler(ty)


def _make_field_unmarshal_obj(
        ctx: UnmarshalFactoryContext,
        ty: ta.Any,
        obj: Unmarshaler | None,
        fac: UnmarshalerFactory | None,
):
    if obj is not None:
        return obj
    if fac is not None:
        if (m := fac.make_unmarshaler(ctx, ty)) is None:
            raise UnhandledTypeError(ty)
        return m()
    return ctx.make_unmarshaler(ty)

##


class AbstractDataclassFactory(lang.Abstract):
    def _get_metadata(self, ty: type) -> ObjectMetadata:
        return get_dataclass_metadata(ty)

    def _get_field_infos(
            self,
            ty: type,
            opts: col.TypeMap[Option] | None = None,
    ) -> FieldInfos:
        return get_dataclass_field_infos(ty, opts)


##


def _type_or_generic_base(rty: rfl.Type) -> type | None:
    if isinstance(rty, rfl.Generic):
        return rty.cls
    elif isinstance(rty, type):
        return rty
    else:
        return None


class DataclassMarshalerFactory(AbstractDataclassFactory, MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (
            (ty := _type_or_generic_base(rty)) is not None and
            dc.is_dataclass(ty) and
            not lang.is_abstract_class(ty)
        ):
            return None

        def inner() -> Marshaler:
            ty = check.isinstance(_type_or_generic_base(rty), type)
            check.state(dc.is_dataclass(ty))
            check.state(not lang.is_abstract_class(ty))

            dc_md = self._get_metadata(ty)
            fis = self._get_field_infos(ty, ctx.options)

            fields = [
                (
                    fi,
                    _make_field_marshal_obj(
                        ctx,
                        fi.type,
                        fi.metadata.marshaler,
                        fi.metadata.marshaler_factory,
                    ),
                )
                for fi in fis
                if fi.name not in dc_md.specials.set
            ]

            return ObjectMarshaler(
                fields,
                specials=dc_md.specials,
            )

        return inner


##


class DataclassUnmarshalerFactory(AbstractDataclassFactory, UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (
            (ty := _type_or_generic_base(rty)) is not None and
            dc.is_dataclass(ty) and
            not lang.is_abstract_class(ty)
        ):
            return None

        def inner() -> Unmarshaler:
            ty = check.isinstance(_type_or_generic_base(rty), type)
            check.state(dc.is_dataclass(ty))
            check.state(not lang.is_abstract_class(ty))

            dc_md = self._get_metadata(ty)
            fis = self._get_field_infos(ty, ctx.options)

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
                    for e_fi in self._get_field_infos(e_ty, ctx.options):
                        e_ns = add_field(e_fi, prefixes=[p + ep for p in prefixes for ep in fi.unmarshal_names])
                        embeds_by_unmarshal_name.update({e_f: (fi.name, e_fi.name) for e_f in e_ns})
                        ret.extend(e_ns)

                else:
                    tup = (
                        fi,
                        _make_field_unmarshal_obj(
                            ctx,
                            fi.type,
                            fi.metadata.unmarshaler,
                            fi.metadata.unmarshaler_factory,
                        ),
                    )

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

        return inner

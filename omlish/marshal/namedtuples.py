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


def _is_named_tuple(rty: rfl.Type) -> bool:
    return (
            isinstance(rty, type) and
            issubclass(rty, tuple) and
            ta.NamedTuple in rfl.get_orig_bases(rty)
    )


##


class NamedtupleMarshalerFactory(MarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return _is_named_tuple(rty)

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


class NamedtupleUnmarshalerFactory(UnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return _is_named_tuple(rty)

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

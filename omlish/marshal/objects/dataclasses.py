"""
TODO:
 - use lang.metadata?
 - clean up names ffs it's not _md anymore
"""
import typing as ta

from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ...lite import marshal as lm
from ..api.configs import Configs
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.errors import UnhandledTypeError
from ..api.naming import Naming
from ..api.naming import translate_name
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from .api import DEFAULT_FIELD_OPTIONS
from .api import DEFAULT_OBJECT_OPTIONS
from .api import FieldOptions
from .api import ObjectOptions
from .infos import FieldInfo
from .infos import FieldInfos
from .marshal import ObjectMarshaler
from .unmarshal import ObjectUnmarshaler


##


def get_dataclass_options(
        ty: type,
        cfgs: Configs | None = None,
) -> ObjectOptions:
    opts = DEFAULT_OBJECT_OPTIONS

    if (md_opts := dc.reflect(ty).spec.metadata_by_type.get(ObjectOptions, [])):
        opts = opts.merge(*md_opts)

    if cfgs is not None and (cfg_opts := cfgs.get(ty).get(ObjectOptions)):
        opts = opts.merge(*cfg_opts)

    return opts


class _FieldInfoBuilder:
    def __init__(
            self,
            ty: type,
            configs: Configs | None = None,
            *,
            dc_rfl: dc.ClassReflection | None = None,
            obj_opts: ObjectOptions | None = None,
    ) -> None:
        self.ty = ty
        self.configs = configs

        if obj_opts is None:
            obj_opts = get_dataclass_options(ty, configs)
        self.obj_md = obj_opts

        fn = self.obj_md.field_naming
        if fn is None and configs is not None:
            if (cn := configs.get(ty).get(Naming)) is None:
                cn = configs.get().get(Naming)
            if cn is not None:
                fn = cn
        self.class_naming = fn

        if dc_rfl is None:
            dc_rfl = dc.reflect(ty)
        self.dc_rfl = dc_rfl

    def build_field_options(self, field: dc.Field) -> FieldOptions:
        """
        Merges configuration from multiple sources in this order (later = higher precedence):
        1. Empty baseline
        2. Class-level field_defaults (from ObjectMetadata)
        3. Field-level FieldMetadata (from field.metadata)
        4. Lite marshal compatibility overrides (OBJ_MARSHALER_FIELD_KEY, etc.)
        5. ObjectOptions.fields
        """

        ##
        # Start with baseline (empty) and merge class-level defaults

        merged_md = DEFAULT_FIELD_OPTIONS.merge(self.obj_md.field_defaults)

        ##
        # Merge field-level FieldMetadata if present

        field_md = field.metadata.get(FieldOptions)
        if field_md is not None:
            merged_md = merged_md.merge(field_md)

        ##
        # Lite marshal compatibility - build override metadata

        lite_override_kw: dict[str, ta.Any] = {}

        # Handle OBJ_MARSHALER_FIELD_KEY
        if lm.OBJ_MARSHALER_FIELD_KEY in field.metadata:
            lfk = field.metadata[lm.OBJ_MARSHALER_FIELD_KEY]
            if lfk is not None:
                check.non_empty_str(lfk)
                lite_override_kw['name'] = lfk
            else:
                lite_override_kw['no_marshal'] = True
                lite_override_kw['no_unmarshal'] = True

        # Handle OBJ_MARSHALER_OMIT_IF_NONE
        if (lon := field.metadata.get(lm.OBJ_MARSHALER_OMIT_IF_NONE)) is not None:
            if check.isinstance(lon, bool):
                lite_override_kw['omit_if'] = lang.is_none

        # Merge lite overrides if any
        if lite_override_kw:
            merged_md = merged_md.merge(FieldOptions(**lite_override_kw))

        ##
        # ObjectOptions

        if (oo_md := (self.obj_md.fields or {}).get(field.name)) is not None:
            merged_md = merged_md.merge(oo_md)

        ##
        # Done

        return merged_md

    def build_field_info(self, field: dc.Field) -> FieldInfo:
        merged_md = self.build_field_options(field)

        ##
        # Determine field type (with generic replacement if needed)

        if self.dc_rfl.spec.generic_init or merged_md.generic_replace:
            f_ty = rfl.to_annotation(self.dc_rfl.fields_inspection.generic_replaced_field_type(field.name))
        else:
            f_ty = self.dc_rfl.type_hints[field.name]

        ##
        # Compute marshal/unmarshal names based on merged metadata

        has_explicit_name = merged_md.name is not None

        marshal_name: str | None
        unmarshal_names: ta.Sequence[str]

        if has_explicit_name:
            # Explicitly set name takes precedence
            # Type narrow: we know merged_md.name is not None here
            explicit_name = check.not_none(merged_md.name)
            marshal_name = explicit_name
            unmarshal_names = col.unique([explicit_name, *(merged_md.alts or ())])
        else:
            # Use naming convention if available, otherwise field name
            field_naming = field.metadata.get(Naming, self.class_naming)
            if field_naming is not None:
                base_name = translate_name(field.name, field_naming)
            else:
                base_name = field.name

            marshal_name = base_name
            unmarshal_names = [base_name]

        ##
        # Handle embed suffix (only if name wasn't explicitly set)

        if merged_md.embed and not has_explicit_name:
            # At this point marshal_name is guaranteed to be str (not None)
            marshal_name = check.not_none(marshal_name) + '_'
            unmarshal_names = [n + '_' for n in unmarshal_names]

        ##
        # Handle no_marshal/no_unmarshal

        if merged_md.no_marshal:
            marshal_name = None
        if merged_md.no_unmarshal:
            unmarshal_names = []

        ##
        # Create FieldInfo with computed values

        return FieldInfo(
            name=field.name,
            type=f_ty,
            marshal_name=marshal_name,
            unmarshal_names=unmarshal_names,
            options=merged_md,
        )

    def build_field_infos(self) -> FieldInfos:
        ret: list[FieldInfo] = []

        for field in self.dc_rfl.instance_fields:
            ret.append(self.build_field_info(field))

        return FieldInfos(ret)


def get_dataclass_field_infos(
        ty: type,
        configs: Configs | None = None,
) -> FieldInfos:
    return _FieldInfoBuilder(ty, configs).build_field_infos()


##


def _type_or_generic_base(rty: rfl.Type) -> type | None:
    if isinstance(rty, rfl.Generic):
        return rty.cls
    elif isinstance(rty, type):
        return rty
    else:
        return None


##


@dc.dataclass()
class _DataclassMarshalerBuilder:
    ctx: MarshalFactoryContext
    rty: rfl.Type

    def build_marshaler(self) -> Marshaler:
        ty = check.isinstance(_type_or_generic_base(self.rty), type)
        check.state(dc.is_dataclass(ty))
        check.state(not lang.is_abstract_class(ty))

        dc_md = get_dataclass_options(ty, self.ctx.configs)
        dc_rfl = dc.reflect(ty)
        fib = _FieldInfoBuilder(ty, self.ctx.configs, dc_rfl=dc_rfl, obj_opts=dc_md)
        fis = fib.build_field_infos()

        fields = [
            (fi, self._make_field_marshal_obj(fi))
            for fi in fis
            if not fi.options.no_marshal
            and fi.name not in dc_md.specials.set
        ]

        unwrap_if_single_field: FieldInfo | None = None
        if dc_md.unwrap_if_single_field in ('marshal', True):
            unwrap_if_single_field = fields[0][0]

        return ObjectMarshaler(
            fields,
            specials=dc_md.specials,
            unwrap_if_single_field=unwrap_if_single_field,
        )

    def _make_field_marshal_obj(self, fi: FieldInfo) -> Marshaler:
        if (obj := fi.options.marshaler) is not None:
            return obj

        if (fac := fi.options.marshaler_factory) is not None:
            if (m := fac.make_marshaler(self.ctx, fi.type)) is None:
                raise UnhandledTypeError(fi.type)
            return m()

        if (as_ := fi.options.marshal_as) is not None:
            return self.ctx.make_marshaler(as_)

        return self.ctx.make_marshaler(fi.type)


class DataclassMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (
            (ty := _type_or_generic_base(rty)) is not None and
            dc.is_dataclass(ty) and
            not lang.is_abstract_class(ty)
        ):
            return None

        def inner() -> Marshaler:
            return _DataclassMarshalerBuilder(ctx, rty).build_marshaler()

        return inner


##


@dc.dataclass()
class _DataclassUnmarshalerBuilder:
    ctx: UnmarshalFactoryContext
    rty: rfl.Type

    #

    _fields_dct: dict[str, tuple[FieldInfo, Unmarshaler]] = dc.field(init=False, default_factory=dict)

    _defaults: dict[str, ta.Any] = dc.field(init=False, default_factory=dict)
    _embeds: dict[str, type] = dc.field(init=False, default_factory=dict)
    _embeds_by_unmarshal_name: dict[str, tuple[str, str]] = dc.field(init=False, default_factory=dict)

    def build_unmarshaler(self) -> Unmarshaler:
        ty = check.isinstance(_type_or_generic_base(self.rty), type)
        check.state(dc.is_dataclass(ty))
        check.state(not lang.is_abstract_class(ty))

        dc_md = get_dataclass_options(ty, self.ctx.configs)
        dc_rfl = dc.reflect(ty)
        fib = _FieldInfoBuilder(ty, self.ctx.configs, dc_rfl=dc_rfl, obj_opts=dc_md)
        fis = fib.build_field_infos()

        for fi in fis:
            if fi.name in dc_md.specials.set:
                continue
            self._add_field(fi)

        unwrap_if_single_field: FieldInfo | None = None
        if dc_md.unwrap_if_single_field in ('unmarshal', True):
            unwrap_if_single_field = next(iter(self._fields_dct.values()))[0]

        return ObjectUnmarshaler(
            ty,
            self._fields_dct,
            specials=dc_md.specials,
            defaults=self._defaults,
            embeds=self._embeds,
            embeds_by_unmarshal_name=self._embeds_by_unmarshal_name,
            ignore_unknown=bool(dc_md.ignore_unknown),
            unwrap_if_single_field=unwrap_if_single_field,
            is_single_field=len(fis) < 2,
        )

    def _add_field(self, fi: FieldInfo, *, prefixes: ta.Iterable[str] = ('',)) -> ta.Iterable[str]:
        if fi.options.no_unmarshal:
            return []

        ret: list[str] = []

        if fi.options.embed:
            e_ty = check.isinstance(fi.type, type)
            check.state(dc.is_dataclass(e_ty))
            e_dc_md = get_dataclass_options(e_ty, self.ctx.configs)
            if e_dc_md.specials.set:
                raise Exception(f'Embedded fields cannot have specials: {e_ty}')

            self._embeds[fi.name] = e_ty
            for e_fi in _FieldInfoBuilder(e_ty, self.ctx.configs).build_field_infos():
                e_ns = self._add_field(e_fi, prefixes=[p + ep for p in prefixes for ep in fi.unmarshal_names])
                self._embeds_by_unmarshal_name.update({e_f: (fi.name, e_fi.name) for e_f in e_ns})
                ret.extend(e_ns)

        else:
            tup = (fi, self._make_field_unmarshal_obj(fi))

            for pfx in prefixes:
                for un in fi.unmarshal_names:
                    un = pfx + un
                    if un in self._fields_dct:
                        raise KeyError(f'Duplicate fields for name {un!r}: {fi.name!r}, {self._fields_dct[un][0].name!r}')  # noqa
                    self._fields_dct[un] = tup
                    ret.append(un)

            if (dfl := fi.options.default) is not None and dfl.present:
                self._defaults[fi.name] = dfl.must()

        return ret

    def _make_field_unmarshal_obj(self, fi: FieldInfo) -> Unmarshaler:
        if (obj := fi.options.unmarshaler) is not None:
            return obj

        if (fac := fi.options.unmarshaler_factory) is not None:
            if (m := fac.make_unmarshaler(self.ctx, fi.type)) is None:
                raise UnhandledTypeError(fi.type)
            return m()

        if (as_ := fi.options.unmarshal_as) is not None:
            return self.ctx.make_unmarshaler(as_)

        return self.ctx.make_unmarshaler(fi.type)


class DataclassUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (
            (ty := _type_or_generic_base(rty)) is not None and
            dc.is_dataclass(ty) and
            not lang.is_abstract_class(ty)
        ):
            return None

        def inner() -> Unmarshaler:
            return _DataclassUnmarshalerBuilder(ctx, rty).build_unmarshaler()

        return inner

"""
TODO:
 - cfg naming
 - adapters for dataclasses / namedtuples / user objects (as configured)
 - mro-merge ObjectMetadata
 - key ordering override - like slice, -1 means last
"""
import collections.abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .naming import Naming
from .values import Value


##


@dc.dataclass(frozen=True, kw_only=True)
class FieldOptions:
    omit_if: ta.Callable[[ta.Any], bool] | None = None

    default: lang.Maybe[ta.Any] = dc.xfield(default=lang.empty(), check_type=lang.Maybe)

    embed: bool = False


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

    field_defaults: FieldMetadata = FieldMetadata()


##


@dc.dataclass(frozen=True, kw_only=True)
class FieldInfo:
    name: str
    type: ta.Any

    marshal_name: str
    unmarshal_names: ta.Sequence[str]

    metadata: FieldMetadata = FieldMetadata()

    options: FieldOptions = FieldOptions()


##


@dc.dataclass(frozen=True)
class ObjectMarshaler(Marshaler):
    fields: ta.Sequence[tuple[FieldInfo, Marshaler]]

    _: dc.KW_ONLY

    unknown_field: str | None = None

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        ret: dict[str, ta.Any] = {}
        for fi, m in self.fields:
            v = getattr(o, fi.name)

            if fi.options.omit_if is not None and fi.options.omit_if(v):
                continue

            mv = m.marshal(ctx, v)

            if fi.options.embed:
                for ek, ev in check.isinstance(mv, collections.abc.Mapping).items():
                    ret[fi.marshal_name + check.non_empty_str(ek)] = ev  # type: ignore

            else:
                ret[fi.marshal_name] = mv

        if self.unknown_field is not None:
            if (ukf := getattr(o, self.unknown_field)):
                if (dks := set(ret) & set(ukf)):
                    raise KeyError(f'Unknown field keys duplicate fields: {dks!r}')

            ret.update(ukf)  # FIXME: marshal?

        return ret


@dc.dataclass(frozen=True)
class SimpleObjectMarshalerFactory(MarshalerFactory):
    dct: ta.Mapping[type, ta.Sequence[FieldInfo]]

    _: dc.KW_ONLY

    unknown_field: str | None = None

    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and rty in self.dct

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        ty = check.isinstance(rty, type)

        flds = self.dct[ty]

        fields = [
            (fi, ctx.make(fi.type))
            for fi in flds
        ]

        return ObjectMarshaler(
            fields,
            unknown_field=self.unknown_field,
        )


##


@dc.dataclass(frozen=True)
class ObjectUnmarshaler(Unmarshaler):
    cls: type
    fields_by_unmarshal_name: ta.Mapping[str, tuple[FieldInfo, Unmarshaler]]

    _: dc.KW_ONLY

    unknown_field: str | None = None

    defaults: ta.Mapping[str, ta.Any] | None = None

    embeds: ta.Mapping[str, type] | None = None
    embeds_by_unmarshal_name: ta.Mapping[str, tuple[str, str]] | None = None

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        ma = check.isinstance(v, collections.abc.Mapping)

        u: ta.Any
        kw: dict[str, ta.Any] = {}
        ukf: dict[str, ta.Any] | None = None

        ekws: dict[str, dict[str, ta.Any]] = {en: {} for en in self.embeds or ()}

        if self.unknown_field is not None:
            kw[self.unknown_field] = ukf = {}

        for k, mv in ma.items():
            ks = check.isinstance(k, str)

            try:
                fi, u = self.fields_by_unmarshal_name[ks]

            except KeyError:
                if ukf is not None:
                    ukf[ks] = mv  # FIXME: unmarshal?
                    continue
                raise

            if self.embeds_by_unmarshal_name and (en := self.embeds_by_unmarshal_name.get(ks)):
                tkw, tk = ekws[en[0]], en[1]
            else:
                tkw, tk = kw, fi.name

            if tk in tkw:
                raise KeyError(f'Duplicate keys for field {tk!r}: {ks!r}')

            tkw[tk] = u.unmarshal(ctx, mv)

        for em, ecls in self.embeds.items() if self.embeds else ():
            ekw = ekws[em]
            ev = ecls(**ekw)
            kw[em] = ev

        if self.defaults:
            for dk, dv in self.defaults.items():
                kw.setdefault(dk, dv)

        return self.cls(**kw)


@dc.dataclass(frozen=True)
class SimpleObjectUnmarshalerFactory(UnmarshalerFactory):
    dct: ta.Mapping[type, ta.Sequence[FieldInfo]]

    _: dc.KW_ONLY

    unknown_field: str | None = None

    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and rty in self.dct

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        ty = check.isinstance(rty, type)

        flds = self.dct[ty]

        fields_by_unmarshal_name = {
            n: (fi, ctx.make(fi.type))
            for fi in flds
            for n in fi.unmarshal_names
        }

        defaults = {
            fi.name: fi.options.default.must()
            for fi in flds
            if fi.options.default.present
        }

        return ObjectUnmarshaler(
            ty,
            fields_by_unmarshal_name,
            unknown_field=self.unknown_field,
            defaults=defaults,
        )

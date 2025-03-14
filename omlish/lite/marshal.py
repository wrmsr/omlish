"""
TODO:
 - pickle stdlib objs? have to pin to 3.8 pickle protocol, will be cross-version
 - literals
 - Options.sequence_cls = list, mapping_cls = dict, ... - def with_mutable_containers() -> Options
"""
# ruff: noqa: UP006 UP007
import abc
import base64
import collections.abc
import dataclasses as dc  # noqa
import datetime
import decimal
import enum
import fractions
import functools
import inspect
import threading
import typing as ta
import uuid
import weakref  # noqa

from .check import check
from .reflect import deep_subclasses
from .reflect import get_literal_type_args
from .reflect import get_new_type_supertype
from .reflect import get_optional_alias_arg
from .reflect import is_generic_alias
from .reflect import is_literal_type
from .reflect import is_new_type
from .reflect import is_union_alias
from .strings import snake_case


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class ObjMarshalOptions:
    raw_bytes: bool = False
    non_strict_fields: bool = False


class ObjMarshaler(abc.ABC):
    @abc.abstractmethod
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        raise NotImplementedError


class NopObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o


@dc.dataclass()
class ProxyObjMarshaler(ObjMarshaler):
    m: ta.Optional[ObjMarshaler] = None

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.not_none(self.m).marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.not_none(self.m).unmarshal(o, ctx)


@dc.dataclass(frozen=True)
class CastObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty(o)


class DynamicObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return ctx.manager.marshal_obj(o, opts=ctx.options)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o


@dc.dataclass(frozen=True)
class Base64ObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return base64.b64encode(o).decode('ascii')

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty(base64.b64decode(o))


@dc.dataclass(frozen=True)
class BytesSwitchedObjMarshaler(ObjMarshaler):
    m: ObjMarshaler

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if ctx.options.raw_bytes:
            return o
        return self.m.marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if ctx.options.raw_bytes:
            return o
        return self.m.unmarshal(o, ctx)


@dc.dataclass(frozen=True)
class EnumObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o.name

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty.__members__[o]  # type: ignore


@dc.dataclass(frozen=True)
class OptionalObjMarshaler(ObjMarshaler):
    item: ObjMarshaler

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if o is None:
            return None
        return self.item.marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if o is None:
            return None
        return self.item.unmarshal(o, ctx)


@dc.dataclass(frozen=True)
class LiteralObjMarshaler(ObjMarshaler):
    item: ObjMarshaler
    vs: frozenset

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.item.marshal(check.in_(o, self.vs), ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.in_(self.item.unmarshal(o, ctx), self.vs)


@dc.dataclass(frozen=True)
class MappingObjMarshaler(ObjMarshaler):
    ty: type
    km: ObjMarshaler
    vm: ObjMarshaler

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return {self.km.marshal(k, ctx): self.vm.marshal(v, ctx) for k, v in o.items()}

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty((self.km.unmarshal(k, ctx), self.vm.unmarshal(v, ctx)) for k, v in o.items())


@dc.dataclass(frozen=True)
class IterableObjMarshaler(ObjMarshaler):
    ty: type
    item: ObjMarshaler

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return [self.item.marshal(e, ctx) for e in o]

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty(self.item.unmarshal(e, ctx) for e in o)


@dc.dataclass(frozen=True)
class FieldsObjMarshaler(ObjMarshaler):
    ty: type

    @dc.dataclass(frozen=True)
    class Field:
        att: str
        key: str
        m: ObjMarshaler

        omit_if_none: bool = False

    fs: ta.Sequence[Field]

    non_strict: bool = False

    #

    _fs_by_att: ta.ClassVar[ta.Mapping[str, Field]]
    _fs_by_key: ta.ClassVar[ta.Mapping[str, Field]]

    def __post_init__(self) -> None:
        fs_by_att: dict = {}
        fs_by_key: dict = {}
        for f in self.fs:
            check.not_in(check.non_empty_str(f.att), fs_by_att)
            check.not_in(check.non_empty_str(f.key), fs_by_key)
            fs_by_att[f.att] = f
            fs_by_key[f.key] = f
        self.__dict__['_fs_by_att'] = fs_by_att
        self.__dict__['_fs_by_key'] = fs_by_key

    #

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        d = {}
        for f in self.fs:
            mv = f.m.marshal(getattr(o, f.att), ctx)
            if mv is None and f.omit_if_none:
                continue
            d[f.key] = mv
        return d

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        kw = {}
        for k, v in o.items():
            if (f := self._fs_by_key.get(k)) is None:
                if not (self.non_strict or ctx.options.non_strict_fields):
                    raise KeyError(k)
                continue
            kw[f.att] = f.m.unmarshal(v, ctx)
        return self.ty(**kw)


@dc.dataclass(frozen=True)
class SingleFieldObjMarshaler(ObjMarshaler):
    ty: type
    fld: str

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return getattr(o, self.fld)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty(**{self.fld: o})


@dc.dataclass(frozen=True)
class PolymorphicObjMarshaler(ObjMarshaler):
    class Impl(ta.NamedTuple):
        ty: type
        tag: str
        m: ObjMarshaler

    impls_by_ty: ta.Mapping[type, Impl]
    impls_by_tag: ta.Mapping[str, Impl]

    @classmethod
    def of(cls, impls: ta.Iterable[Impl]) -> 'PolymorphicObjMarshaler':
        return cls(
            {i.ty: i for i in impls},
            {i.tag: i for i in impls},
        )

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        impl = self.impls_by_ty[type(o)]
        return {impl.tag: impl.m.marshal(o, ctx)}

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        [(t, v)] = o.items()
        impl = self.impls_by_tag[t]
        return impl.m.unmarshal(v, ctx)


@dc.dataclass(frozen=True)
class DatetimeObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o.isoformat()

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self.ty.fromisoformat(o)  # type: ignore


class DecimalObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return str(check.isinstance(o, decimal.Decimal))

    def unmarshal(self, v: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return decimal.Decimal(check.isinstance(v, str))


class FractionObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        fr = check.isinstance(o, fractions.Fraction)
        return [fr.numerator, fr.denominator]

    def unmarshal(self, v: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        num, denom = check.isinstance(v, list)
        return fractions.Fraction(num, denom)


class UuidObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return str(o)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return uuid.UUID(o)


##


_DEFAULT_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
    **{t: NopObjMarshaler() for t in (type(None),)},
    **{t: CastObjMarshaler(t) for t in (int, float, str, bool)},
    **{t: BytesSwitchedObjMarshaler(Base64ObjMarshaler(t)) for t in (bytes, bytearray)},
    **{t: IterableObjMarshaler(t, DynamicObjMarshaler()) for t in (list, tuple, set, frozenset)},
    **{t: MappingObjMarshaler(t, DynamicObjMarshaler(), DynamicObjMarshaler()) for t in (dict,)},

    **{t: DynamicObjMarshaler() for t in (ta.Any, object)},

    **{t: DatetimeObjMarshaler(t) for t in (datetime.date, datetime.time, datetime.datetime)},
    decimal.Decimal: DecimalObjMarshaler(),
    fractions.Fraction: FractionObjMarshaler(),
    uuid.UUID: UuidObjMarshaler(),
}

_OBJ_MARSHALER_GENERIC_MAPPING_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (dict,)},
    **{t: dict for t in (collections.abc.Mapping, collections.abc.MutableMapping)},  # noqa
}

_OBJ_MARSHALER_GENERIC_ITERABLE_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (list, tuple, set, frozenset)},
    collections.abc.Set: frozenset,
    collections.abc.MutableSet: set,
    collections.abc.Sequence: tuple,
    collections.abc.MutableSequence: list,
}


##


_REGISTERED_OBJ_MARSHALERS_BY_TYPE: ta.MutableMapping[type, ObjMarshaler] = weakref.WeakKeyDictionary()


def register_type_obj_marshaler(ty: type, om: ObjMarshaler) -> None:
    _REGISTERED_OBJ_MARSHALERS_BY_TYPE[ty] = om


def register_single_field_type_obj_marshaler(fld, ty=None):
    def inner(ty):  # noqa
        register_type_obj_marshaler(ty, SingleFieldObjMarshaler(ty, fld))
        return ty

    if ty is not None:
        return inner(ty)
    else:
        return inner


##


class ObjMarshalerFieldMetadata:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


class OBJ_MARSHALER_FIELD_KEY(ObjMarshalerFieldMetadata):  # noqa
    pass


class OBJ_MARSHALER_OMIT_IF_NONE(ObjMarshalerFieldMetadata):  # noqa
    pass


##


class ObjMarshalerManager:
    def __init__(
            self,
            *,
            default_options: ObjMarshalOptions = ObjMarshalOptions(),

            default_obj_marshalers: ta.Dict[ta.Any, ObjMarshaler] = _DEFAULT_OBJ_MARSHALERS,  # noqa
            generic_mapping_types: ta.Dict[ta.Any, type] = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES,  # noqa
            generic_iterable_types: ta.Dict[ta.Any, type] = _OBJ_MARSHALER_GENERIC_ITERABLE_TYPES,  # noqa

            registered_obj_marshalers: ta.Mapping[type, ObjMarshaler] = _REGISTERED_OBJ_MARSHALERS_BY_TYPE,
    ) -> None:
        super().__init__()

        self._default_options = default_options

        self._obj_marshalers = dict(default_obj_marshalers)
        self._generic_mapping_types = generic_mapping_types
        self._generic_iterable_types = generic_iterable_types
        self._registered_obj_marshalers = registered_obj_marshalers

        self._lock = threading.RLock()
        self._marshalers: ta.Dict[ta.Any, ObjMarshaler] = dict(_DEFAULT_OBJ_MARSHALERS)
        self._proxies: ta.Dict[ta.Any, ProxyObjMarshaler] = {}

    #

    def make_obj_marshaler(
            self,
            ty: ta.Any,
            rec: ta.Callable[[ta.Any], ObjMarshaler],
            *,
            non_strict_fields: bool = False,
    ) -> ObjMarshaler:
        if isinstance(ty, type):
            if (reg := self._registered_obj_marshalers.get(ty)) is not None:
                return reg

            if abc.ABC in ty.__bases__:
                tn = ty.__name__
                impls: ta.List[ta.Tuple[type, str]] = [  # type: ignore[var-annotated]
                    (ity, ity.__name__)
                    for ity in deep_subclasses(ty)
                    if abc.ABC not in ity.__bases__
                ]

                if all(itn.endswith(tn) for _, itn in impls):
                    impls = [
                        (ity, snake_case(itn[:-len(tn)]))
                        for ity, itn in impls
                    ]

                dupe_tns = sorted(
                    dn
                    for dn, dc in collections.Counter(itn for _, itn in impls).items()
                    if dc > 1
                )
                if dupe_tns:
                    raise KeyError(f'Duplicate impl names for {ty}: {dupe_tns}')

                return PolymorphicObjMarshaler.of([
                    PolymorphicObjMarshaler.Impl(
                        ity,
                        itn,
                        rec(ity),
                    )
                    for ity, itn in impls
                ])

            if issubclass(ty, enum.Enum):
                return EnumObjMarshaler(ty)

            if dc.is_dataclass(ty):
                return FieldsObjMarshaler(
                    ty,
                    [
                        FieldsObjMarshaler.Field(
                            att=f.name,
                            key=check.non_empty_str(fk),
                            m=rec(f.type),
                            omit_if_none=check.isinstance(f.metadata.get(OBJ_MARSHALER_OMIT_IF_NONE, False), bool),
                        )
                        for f in dc.fields(ty)
                        if (fk := f.metadata.get(OBJ_MARSHALER_FIELD_KEY, f.name)) is not None
                    ],
                    non_strict=non_strict_fields,
                )

            if issubclass(ty, tuple) and hasattr(ty, '_fields'):
                return FieldsObjMarshaler(
                    ty,
                    [
                        FieldsObjMarshaler.Field(
                            att=p.name,
                            key=p.name,
                            m=rec(p.annotation),
                        )
                        for p in inspect.signature(ty).parameters.values()
                    ],
                    non_strict=non_strict_fields,
                )

        if is_new_type(ty):
            return rec(get_new_type_supertype(ty))

        if is_literal_type(ty):
            lvs = frozenset(get_literal_type_args(ty))
            lty = check.single(set(map(type, lvs)))
            return LiteralObjMarshaler(rec(lty), lvs)

        if is_generic_alias(ty):
            try:
                mt = self._generic_mapping_types[ta.get_origin(ty)]
            except KeyError:
                pass
            else:
                k, v = ta.get_args(ty)
                return MappingObjMarshaler(mt, rec(k), rec(v))

            try:
                st = self._generic_iterable_types[ta.get_origin(ty)]
            except KeyError:
                pass
            else:
                [e] = ta.get_args(ty)
                return IterableObjMarshaler(st, rec(e))

            if is_union_alias(ty):
                return OptionalObjMarshaler(rec(get_optional_alias_arg(ty)))

        raise TypeError(ty)

    #

    def set_obj_marshaler(
            self,
            ty: ta.Any,
            m: ObjMarshaler,
            *,
            override: bool = False,
    ) -> None:
        with self._lock:
            if not override and ty in self._obj_marshalers:
                raise KeyError(ty)
            self._obj_marshalers[ty] = m

    def get_obj_marshaler(
            self,
            ty: ta.Any,
            *,
            no_cache: bool = False,
            **kwargs: ta.Any,
    ) -> ObjMarshaler:
        with self._lock:
            if not no_cache:
                try:
                    return self._obj_marshalers[ty]
                except KeyError:
                    pass

            try:
                return self._proxies[ty]
            except KeyError:
                pass

            rec = functools.partial(
                self.get_obj_marshaler,
                no_cache=no_cache,
                **kwargs,
            )

            p = ProxyObjMarshaler()
            self._proxies[ty] = p
            try:
                m = self.make_obj_marshaler(ty, rec, **kwargs)
            finally:
                del self._proxies[ty]
            p.m = m

            if not no_cache:
                self._obj_marshalers[ty] = m
            return m

    #

    def _make_context(self, opts: ta.Optional[ObjMarshalOptions]) -> 'ObjMarshalContext':
        return ObjMarshalContext(
            options=opts or self._default_options,
            manager=self,
        )

    def marshal_obj(
            self,
            o: ta.Any,
            ty: ta.Any = None,
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> ta.Any:
        m = self.get_obj_marshaler(ty if ty is not None else type(o))
        return m.marshal(o, self._make_context(opts))

    def unmarshal_obj(
            self,
            o: ta.Any,
            ty: ta.Union[ta.Type[T], ta.Any],
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> T:
        m = self.get_obj_marshaler(ty)
        return m.unmarshal(o, self._make_context(opts))

    def roundtrip_obj(
            self,
            o: ta.Any,
            ty: ta.Any = None,
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> ta.Any:
        if ty is None:
            ty = type(o)
        m: ta.Any = self.marshal_obj(o, ty, opts)
        u: ta.Any = self.unmarshal_obj(m, ty, opts)
        return u


@dc.dataclass(frozen=True)
class ObjMarshalContext:
    options: ObjMarshalOptions
    manager: ObjMarshalerManager


##


OBJ_MARSHALER_MANAGER = ObjMarshalerManager()

set_obj_marshaler = OBJ_MARSHALER_MANAGER.set_obj_marshaler
get_obj_marshaler = OBJ_MARSHALER_MANAGER.get_obj_marshaler

marshal_obj = OBJ_MARSHALER_MANAGER.marshal_obj
unmarshal_obj = OBJ_MARSHALER_MANAGER.unmarshal_obj

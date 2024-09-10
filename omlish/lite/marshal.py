"""
TODO:
 - pickle stdlib objs? have to pin to 3.8 pickle protocol, will be cross-version
 - nonstrict toggle
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
import typing as ta
import uuid
import weakref  # noqa

from .check import check_isinstance
from .check import check_not_none
from .reflect import deep_subclasses
from .reflect import get_optional_alias_arg
from .reflect import is_generic_alias
from .reflect import is_union_alias


T = ta.TypeVar('T')


##


class ObjMarshaler(abc.ABC):
    @abc.abstractmethod
    def marshal(self, o: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def unmarshal(self, o: ta.Any) -> ta.Any:
        raise NotImplementedError


class NopObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return o


@dc.dataclass()
class ProxyObjMarshaler(ObjMarshaler):
    m: ta.Optional[ObjMarshaler] = None

    def marshal(self, o: ta.Any) -> ta.Any:
        return check_not_none(self.m).marshal(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return check_not_none(self.m).unmarshal(o)


@dc.dataclass(frozen=True)
class CastObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(o)


class DynamicObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return marshal_obj(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return o


@dc.dataclass(frozen=True)
class Base64ObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return base64.b64encode(o).decode('ascii')

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(base64.b64decode(o))


@dc.dataclass(frozen=True)
class EnumObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return o.name

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty.__members__[o]  # type: ignore


@dc.dataclass(frozen=True)
class OptionalObjMarshaler(ObjMarshaler):
    item: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        if o is None:
            return None
        return self.item.marshal(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        if o is None:
            return None
        return self.item.unmarshal(o)


@dc.dataclass(frozen=True)
class MappingObjMarshaler(ObjMarshaler):
    ty: type
    km: ObjMarshaler
    vm: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        return {self.km.marshal(k): self.vm.marshal(v) for k, v in o.items()}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty((self.km.unmarshal(k), self.vm.unmarshal(v)) for k, v in o.items())


@dc.dataclass(frozen=True)
class IterableObjMarshaler(ObjMarshaler):
    ty: type
    item: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        return [self.item.marshal(e) for e in o]

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(self.item.unmarshal(e) for e in o)


@dc.dataclass(frozen=True)
class DataclassObjMarshaler(ObjMarshaler):
    ty: type
    fs: ta.Mapping[str, ObjMarshaler]
    nonstrict: bool = False

    def marshal(self, o: ta.Any) -> ta.Any:
        return {k: m.marshal(getattr(o, k)) for k, m in self.fs.items()}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(**{k: self.fs[k].unmarshal(v) for k, v in o.items() if self.nonstrict or k in self.fs})


@dc.dataclass(frozen=True)
class PolymorphicObjMarshaler(ObjMarshaler):
    class Impl(ta.NamedTuple):
        ty: type
        tag: str
        m: ObjMarshaler

    impls_by_ty: ta.Mapping[type, Impl]
    impls_by_tag: ta.Mapping[str, Impl]

    def marshal(self, o: ta.Any) -> ta.Any:
        impl = self.impls_by_ty[type(o)]
        return {impl.tag: impl.m.marshal(o)}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        [(t, v)] = o.items()
        impl = self.impls_by_tag[t]
        return impl.m.unmarshal(v)


@dc.dataclass(frozen=True)
class DatetimeObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return o.isoformat()

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty.fromisoformat(o)  # type: ignore


class DecimalObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return str(check_isinstance(o, decimal.Decimal))

    def unmarshal(self, v: ta.Any) -> ta.Any:
        return decimal.Decimal(check_isinstance(v, str))


class FractionObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        fr = check_isinstance(o, fractions.Fraction)
        return [fr.numerator, fr.denominator]

    def unmarshal(self, v: ta.Any) -> ta.Any:
        num, denom = check_isinstance(v, list)
        return fractions.Fraction(num, denom)


class UuidObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return str(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return uuid.UUID(o)


_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
    **{t: NopObjMarshaler() for t in (type(None),)},
    **{t: CastObjMarshaler(t) for t in (int, float, str, bool)},
    **{t: Base64ObjMarshaler(t) for t in (bytes, bytearray)},
    **{t: IterableObjMarshaler(t, DynamicObjMarshaler()) for t in (list, tuple, set, frozenset)},
    **{t: MappingObjMarshaler(t, DynamicObjMarshaler(), DynamicObjMarshaler()) for t in (dict,)},

    ta.Any: DynamicObjMarshaler(),

    **{t: DatetimeObjMarshaler(t) for t in (datetime.date, datetime.time, datetime.datetime)},
    decimal.Decimal: DecimalObjMarshaler(),
    fractions.Fraction: FractionObjMarshaler(),
    uuid.UUID: UuidObjMarshaler(),
}

_OBJ_MARSHALER_GENERIC_MAPPING_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (dict,)},
    **{t: dict for t in (collections.abc.Mapping, collections.abc.MutableMapping)},
}

_OBJ_MARSHALER_GENERIC_ITERABLE_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (list, tuple, set, frozenset)},
    collections.abc.Set: frozenset,
    collections.abc.MutableSet: set,
    collections.abc.Sequence: tuple,
    collections.abc.MutableSequence: list,
}


def register_opj_marshaler(ty: ta.Any, m: ObjMarshaler) -> None:
    if ty in _OBJ_MARSHALERS:
        raise KeyError(ty)
    _OBJ_MARSHALERS[ty] = m


def _make_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    if isinstance(ty, type) and abc.ABC in ty.__bases__:
        impls = [  # type: ignore
            PolymorphicObjMarshaler.Impl(
                ity,
                ity.__qualname__,
                get_obj_marshaler(ity),
            )
            for ity in deep_subclasses(ty)
            if abc.ABC not in ity.__bases__
        ]
        return PolymorphicObjMarshaler(
            {i.ty: i for i in impls},
            {i.tag: i for i in impls},
        )

    if isinstance(ty, type) and issubclass(ty, enum.Enum):
        return EnumObjMarshaler(ty)

    if dc.is_dataclass(ty):
        return DataclassObjMarshaler(
            ty,
            {f.name: get_obj_marshaler(f.type) for f in dc.fields(ty)},
        )

    if is_generic_alias(ty):
        try:
            mt = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            k, v = ta.get_args(ty)
            return MappingObjMarshaler(mt, get_obj_marshaler(k), get_obj_marshaler(v))

        try:
            st = _OBJ_MARSHALER_GENERIC_ITERABLE_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            [e] = ta.get_args(ty)
            return IterableObjMarshaler(st, get_obj_marshaler(e))

        if is_union_alias(ty):
            return OptionalObjMarshaler(get_obj_marshaler(get_optional_alias_arg(ty)))

    raise TypeError(ty)


def get_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    try:
        return _OBJ_MARSHALERS[ty]
    except KeyError:
        pass

    p = ProxyObjMarshaler()
    _OBJ_MARSHALERS[ty] = p
    try:
        m = _make_obj_marshaler(ty)
    except Exception:
        del _OBJ_MARSHALERS[ty]
        raise
    else:
        p.m = m
        _OBJ_MARSHALERS[ty] = m
        return m


def marshal_obj(o: ta.Any, ty: ta.Any = None) -> ta.Any:
    return get_obj_marshaler(ty if ty is not None else type(o)).marshal(o)


def unmarshal_obj(o: ta.Any, ty: ta.Union[ta.Type[T], ta.Any]) -> T:
    return get_obj_marshaler(ty).unmarshal(o)

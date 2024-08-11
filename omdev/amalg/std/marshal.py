# ruff: noqa: UP006
import abc
import base64
import collections.abc
import dataclasses as dc  # noqa
import datetime
import typing as ta
import uuid
import weakref  # noqa

from .reflect import is_generic_alias


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
class SequenceObjMarshaler(ObjMarshaler):
    ty: type
    item: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        return [self.item.marshal(e) for e in o]

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(self.item.unmarshal(e) for e in o)


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
class DataclassObjMarshaler(ObjMarshaler):
    ty: type
    fs: ta.Mapping[str, ObjMarshaler]

    def marshal(self, o: ta.Any) -> ta.Any:
        return {k: m.marshal(getattr(o, k)) for k, m in self.fs.items()}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(**{k: m.unmarshal(o[k]) for k, m in self.fs.items()})


class DatetimeObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return o.isoformat()

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return datetime.datetime.fromisoformat(o)


class UuidObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return str(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return uuid.UUID(o)


_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
    **{t: NopObjMarshaler() for t in (type(None),)},
    **{t: CastObjMarshaler(t) for t in (int, float, str)},
    **{t: Base64ObjMarshaler(t) for t in (bytes, bytearray)},
    **{t: SequenceObjMarshaler(t, DynamicObjMarshaler()) for t in (list, tuple, set, frozenset)},
    **{t: MappingObjMarshaler(t, DynamicObjMarshaler(), DynamicObjMarshaler()) for t in (dict,)},

    datetime.datetime: DatetimeObjMarshaler(),
    uuid.UUID: UuidObjMarshaler(),
}


_OBJ_MARSHALER_GENERIC_SEQUENCE_TYPES = {
    **{t: t for t in (list, tuple, set, frozenset)},
    **{t: frozenset for t in (collections.abc.Set, collections.abc.MutableSet)},
    **{t: tuple for t in (collections.abc.Sequence, collections.abc.MutableSequence)},
}

_OBJ_MARSHALER_GENERIC_MAPPING_TYPES = {
    **{t: t for t in (dict,)},
    **{t: dict for t in (collections.abc.Mapping, collections.abc.MutableMapping)},
}


def _make_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    if dc.is_dataclass(ty):
        return DataclassObjMarshaler(
            ty,
            {f.name: get_obj_marshaler(f.type) for f in dc.fields(ty)},
        )

    if is_generic_alias(ty):
        try:
            st = _OBJ_MARSHALER_GENERIC_SEQUENCE_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            [e] = ta.get_args(ty)
            return SequenceObjMarshaler(st, get_obj_marshaler(e))

        try:
            mt = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            k, v = ta.get_args(ty)
            return MappingObjMarshaler(mt, get_obj_marshaler(k), get_obj_marshaler(v))

    raise TypeError(ty)


def get_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    try:
        return _OBJ_MARSHALERS[ty]
    except KeyError:
        pass
    m = _OBJ_MARSHALERS[ty] = _make_obj_marshaler(ty)
    return m


def marshal_obj(o: ta.Any, ty: ta.Any = None) -> ta.Any:
    return get_obj_marshaler(ty if ty is not None else type(o)).marshal(o)


def unmarshal_obj(o: ta.Any, ty: ta.Any) -> ta.Any:
    return get_obj_marshaler(ty).unmarshal(o)

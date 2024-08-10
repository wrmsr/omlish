# ruff: noqa: UP006
import abc
import base64
import dataclasses as dc  # noqa
import datetime
import typing as ta
import uuid
import weakref  # noqa


MARSHAL_BUILTIN_TYPES = (
    float,
    int,
    str,
    type(None),
)


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


class DynamicObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return marshal_obj(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return o


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
class DataclassObjMarshaler(ObjMarshaler):
    ty: type
    fs: ta.Mapping[str, ObjMarshaler]

    def marshal(self, o: ta.Any) -> ta.Any:
        return {k: m.marshal(getattr(o, k)) for k, m in self.fs.items()}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(**{k: m.unmarshal(o[k]) for k, m in self.fs.items()})


_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
    **{t: NopObjMarshaler() for t in MARSHAL_BUILTIN_TYPES},
    uuid.UUID: UuidObjMarshaler(),
    datetime.datetime: DatetimeObjMarshaler(),
    **{t: Base64ObjMarshaler(t) for t in (bytes, bytearray)},
    list: SequenceObjMarshaler(list, DynamicObjMarshaler()),
}


def get_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    try:
        return _OBJ_MARSHALERS[ty]
    except KeyError:
        pass

    m: ObjMarshaler

    if dc.is_dataclass(ty):
        m = DataclassObjMarshaler(
            ty,
            {f.name: get_obj_marshaler(f.type) for f in dc.fields(ty)},
        )

    else:
        raise TypeError(ty)

    _OBJ_MARSHALERS[ty] = m
    return m


def marshal_obj(o: ta.Any, ty: ta.Any = None) -> ta.Any:
    return get_obj_marshaler(ty if ty is not None else type(o)).marshal(o)


def unmarshal_obj(o: ta.Any, ty: ta.Any) -> ta.Any:
    return get_obj_marshaler(ty).unmarshal(o)

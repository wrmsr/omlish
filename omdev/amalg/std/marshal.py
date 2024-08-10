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


_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
    **{t: NopObjMarshaler() for t in MARSHAL_BUILTIN_TYPES},
    uuid.UUID: UuidObjMarshaler(),
    datetime.datetime: DatetimeObjMarshaler(),
    **{t: Base64ObjMarshaler(t) for t in (bytes, bytearray)},
}


def get_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    try:
        return _OBJ_MARSHALERS[ty]
    except KeyError:
        raise TypeError(ty)  # noqa


def marshal_obj(o: ta.Any, ty: ta.Any = None) -> ta.Any:
    return get_obj_marshaler(ty if ty is not None else type(o)).marshal(o)


def unmarshal_obj(o: ta.Any, ty: ta.Any) -> ta.Any:
    return get_obj_marshaler(ty).unmarshal(o)

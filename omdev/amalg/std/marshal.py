import abc
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
    def unmarshal(self, o: ta.Any, ty: ta.Any) -> ta.Any:
        raise NotImplementedError


class NopObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any, ty: ta.Any) -> ta.Any:
        return o


class UuidObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return str(o)

    def unmarshal(self, o: ta.Any, ty: ta.Any) -> ta.Any:
        return uuid.UUID(o)


@dc.dataclass(frozen=True)
class OptionalObjMarshaler(ObjMarshaler):
    item: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        if o is None:
            return None
        return self.item.marshal(o)

    def unmarshal(self, o: ta.Any, ty: ta.Any) -> ta.Any:
        if o is None:
            return None
        return self.item.unmarshal(o, ty)


def marshal_obj(o: ta.Any) -> ta.Any:
    if isinstance(o, MARSHAL_BUILTIN_TYPES):
        return o

    if isinstance(o, datetime.datetime):
        return o.isoformat()

    if isinstance(o, uuid.UUID):
        return str(o)

    raise TypeError(o)


def unmarshal_obj(o: ta.Any, ty: ta.Any) -> ta.Any:
    if ty in MARSHAL_BUILTIN_TYPES:
        return o

    if ty is datetime.datetime:
        return datetime.datetime.fromisoformat(o)

    if ty is uuid.UUID:
        return uuid.UUID(o)

    raise TypeError(o)

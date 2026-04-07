import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .. import marshal as msh
from .. import reflect as rfl
from .. import typedvalues as tv
from ..formats import json
from .fields import FieldOption


##


@ta.final
@dc.dataclass(frozen=True)
class FieldCodec(tv.UniqueTypedValue, FieldOption, lang.Final):
    v: 'Codec'


##


class Codec(lang.Abstract):
    @abc.abstractmethod
    def encode(self, obj: ta.Any, rty: rfl.Type) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self, val: ta.Any, rty: rfl.Type) -> ta.Any:
        raise NotImplementedError


@ta.final
class NopCodec(Codec):
    def encode(self, obj: ta.Any, rty: rfl.Type) -> ta.Any:
        return obj

    def decode(self, val: ta.Any, rty: rfl.Type) -> ta.Any:
        return val


@ta.final
class FnCodec(Codec):
    def __init__(
            self,
            encode: ta.Callable[[ta.Any, rfl.Type], ta.Any],
            decode: ta.Callable[[ta.Any, rfl.Type], ta.Any],
    ) -> None:
        super().__init__()

        self._encode = encode
        self._decode = decode

    def encode(self, obj: ta.Any, rty: rfl.Type) -> ta.Any:
        return self._encode(obj, rty)

    def decode(self, val: ta.Any, rty: rfl.Type) -> ta.Any:
        return self._decode(val, rty)


@ta.final
class OptionalCodec(Codec):
    def __init__(self, child: Codec) -> None:
        super().__init__()

        self._child = child

    def encode(self, obj: ta.Any, rty: rfl.Type) -> ta.Any:
        if obj is None:
            return None
        return self._child.encode(obj, rty)

    def decode(self, val: ta.Any, rty: rfl.Type) -> ta.Any:
        if val is None:
            return None
        return self._child.decode(val, rty)


@ta.final
class CompositeCodec(Codec):
    def __init__(self, *children: Codec) -> None:
        super().__init__()

        self._children = children

    def encode(self, obj: ta.Any, rty: rfl.Type) -> ta.Any:
        for child in self._children:
            obj = child.encode(obj, rty)
        return obj

    def decode(self, val: ta.Any, rty: rfl.Type) -> ta.Any:
        for child in reversed(self._children):
            val = child.decode(val, rty)
        return val


##


@ta.final
class JsonCodec(Codec):
    def encode(self, obj: ta.Any, rty: rfl.Type) -> ta.Any:
        return json.dumps_compact(obj)

    def decode(self, val: ta.Any, rty: rfl.Type) -> ta.Any:
        return json.loads(val)


@ta.final
class MarshalCodec(Codec):
    def encode(self, obj: ta.Any, rty: rfl.Type) -> ta.Any:
        return msh.marshal(obj, rty)

    def decode(self, val: ta.Any, rty: rfl.Type) -> ta.Any:
        return msh.unmarshal(val, rty)

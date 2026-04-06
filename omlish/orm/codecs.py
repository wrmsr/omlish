import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .. import marshal as msh
from .. import reflect as rfl
from .. import typedvalues as tv
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


##


@ta.final
class MarshalCodec(Codec):
    def encode(self, obj: ta.Any, rty: rfl.Type) -> ta.Any:
        return msh.marshal(obj, rty)

    def decode(self, val: ta.Any, rty: rfl.Type) -> ta.Any:
        return msh.unmarshal(val, rty)

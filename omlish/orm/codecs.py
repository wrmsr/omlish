# ruff: noqa: SLF001
import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .. import marshal as msh
from .. import reflect as rfl
from .. import typedvalues as tv
from ..formats import json
from .fields import Field
from .fields import FieldOption


if ta.TYPE_CHECKING:
    from .mappers import Mapper

##


@ta.final
@dc.dataclass(frozen=True)
class FieldCodec(tv.UniqueTypedValue, FieldOption, lang.Final):
    v: Codec


##


CodecSubject: ta.TypeAlias = ta.Union[  # noqa
    Field,
    'Mapper',
]


class Codec(lang.Abstract):
    @abc.abstractmethod
    def encode(self, obj: ta.Any, cs: CodecSubject) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self, val: ta.Any, cs: CodecSubject) -> ta.Any:
        raise NotImplementedError

    #

    @staticmethod
    def rty(cs: CodecSubject) -> rfl.Type:
        if cs.__class__ is Field:
            return cs.unwrapped_rty
        else:
            return cs._cls  # type: ignore[union-attr]


@ta.final
class NopCodec(Codec):
    def encode(self, obj: ta.Any, cs: CodecSubject) -> ta.Any:
        return obj

    def decode(self, val: ta.Any, cs: CodecSubject) -> ta.Any:
        return val


@ta.final
class OptionalCodec(Codec):
    def __init__(self, child: Codec) -> None:
        super().__init__()

        self._child = child

    def encode(self, obj: ta.Any, cs: CodecSubject) -> ta.Any:
        if obj is None:
            return None
        return self._child.encode(obj, cs)

    def decode(self, val: ta.Any, cs: CodecSubject) -> ta.Any:
        if val is None:
            return None
        return self._child.decode(val, cs)


@ta.final
class CompositeCodec(Codec):
    def __init__(self, *children: Codec) -> None:
        super().__init__()

        self._children = children

    def encode(self, obj: ta.Any, cs: CodecSubject) -> ta.Any:
        for child in self._children:
            obj = child.encode(obj, cs)
        return obj

    def decode(self, val: ta.Any, cs: CodecSubject) -> ta.Any:
        for child in reversed(self._children):
            val = child.decode(val, cs)
        return val


##


@ta.final
class JsonCodec(Codec):
    def encode(self, obj: ta.Any, cs: CodecSubject) -> ta.Any:
        return json.dumps_compact(obj)

    def decode(self, val: ta.Any, cs: CodecSubject) -> ta.Any:
        return json.loads(val)


@ta.final
class MarshalCodec(Codec):
    def encode(self, obj: ta.Any, cs: CodecSubject) -> ta.Any:
        return msh.marshal(obj, self.rty(cs))

    def decode(self, val: ta.Any, cs: CodecSubject) -> ta.Any:
        return msh.unmarshal(val, self.rty(cs))

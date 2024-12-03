"""
TODO:
 - bytes-like - bytearray, memoryview
"""
import abc
import dataclasses as dc
import typing as ta

from omlish import lang
from omlish import reflect as rfl


I = ta.TypeVar('I')
O = ta.TypeVar('O')


##


class EagerCodec(lang.Abstract, ta.Generic[I, O]):
    @abc.abstractmethod
    def encode(self, i: I) -> O:
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self, o: O) -> I:
        raise NotImplementedError


class IncrementalCodec(lang.Abstract, ta.Generic[I, O]):
    @abc.abstractmethod
    def iterencode(self) -> ta.Generator[O | None, I, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def iterdecode(self) -> ta.Generator[I | None, O, None]:
        raise NotImplementedError


class ComboCodec(  # noqa
    EagerCodec[I, O],
    IncrementalCodec[I, O],
    lang.Abstract,
    ta.Generic[I, O],
):
    pass


##


@dc.dataclass(frozen=True, kw_only=True)
class Codec(lang.Final):
    name: str
    aliases: ta.Collection[str] | None = None

    input: rfl.Type
    output: rfl.Type

    options: type | None = None

    new: ta.Callable[..., EagerCodec]
    new_incremental: ta.Callable[..., IncrementalCodec] | None = None

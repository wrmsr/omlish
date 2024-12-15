"""
TODO:
 - bytes-like - bytearray, memoryview
"""
import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
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
    def encode_incremental(self) -> ta.Generator[O | None, I, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def decode_incremental(self) -> ta.Generator[I | None, O, None]:
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
class Codec:
    name: str = dc.field(validate=check.non_empty_str)
    aliases: ta.Collection[str] | None = dc.field(default=None, validate=check.of_not_isinstance(str))

    input: rfl.Type
    output: rfl.Type

    options: type | None = None

    new: ta.Callable[..., EagerCodec]
    new_incremental: ta.Callable[..., IncrementalCodec] | None = None

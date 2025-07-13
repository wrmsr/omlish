import dataclasses as dc
import typing as ta

from ..funcs import pairs as fps
from .base import EagerCodec


I = ta.TypeVar('I')
O = ta.TypeVar('O')


##


@dc.dataclass(frozen=True)
class FnPairEagerCodec(EagerCodec[I, O]):
    fp: fps.FnPair[I, O]

    def encode(self, i: I) -> O:
        return self.fp.forward(i)

    def decode(self, o: O) -> I:
        return self.fp.backward(o)

    @classmethod
    def of(
            cls,
            encode: ta.Callable[[I], O],
            decode: ta.Callable[[O], I],
    ) -> 'FnPairEagerCodec[I, O]':
        return cls(fps.of(encode, decode))


def of_pair(fp: fps.FnPair[I, O]) -> FnPairEagerCodec[I, O]:
    return FnPairEagerCodec(fp)


def of(
        encode: ta.Callable[[I], O],
        decode: ta.Callable[[O], I],
) -> FnPairEagerCodec[I, O]:
    return FnPairEagerCodec(fps.of(encode, decode))

import dataclasses as dc
import typing as ta

from .base import EagerCodec


##


@dc.dataclass(frozen=True)
class ChainEagerCodec(EagerCodec[ta.Any, ta.Any]):
    codecs: ta.Sequence[EagerCodec]

    def encode(self, v: ta.Any) -> ta.Any:
        for c in self.codecs:
            v = c.encode(v)
        return v

    def decode(self, v: ta.Any) -> ta.Any:
        for c in reversed(self.codecs):
            v = c.decode(v)
        return v


def chain(*codecs: EagerCodec) -> ChainEagerCodec:
    return ChainEagerCodec(codecs)

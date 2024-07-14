"""
TODO:
 - tame the block/stream/fileobj divergence in codecs and elsewhere
  - https://docs.python.org/3/library/codecs.html#incremental-encoding-and-decoding
  - as well as push/pull(/async now)
 - interops
  - csvloader
"""
import abc
import typing as ta


F = ta.TypeVar('F')
T = ta.TypeVar('T')


class Encoder(ta.Generic[F, T]):

    @abc.abstractmethod
    def encode(self, obj: F) -> T:
        raise NotImplementedError


class Decoder(ta.Generic[F, T]):

    @abc.abstractmethod
    def decode(self, obj: T) -> F:
        raise NotImplementedError


class Codec(Encoder[F, T], Decoder[F, T]):
    pass

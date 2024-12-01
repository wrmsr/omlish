import abc
import typing as ta


I = ta.TypeVar('I')
O = ta.TypeVar('O')


##


class Codec:
    pass


class EagerCodec(Codec, ta.Generic[I, O]):
    @abc.abstractmethod
    def encode(self, i: I) -> O:
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self, o: O) -> I:
        raise NotImplementedError


class IncrementalCodec(Codec):
    @abc.abstractmethod
    def iter_encode(self) -> ta.Generator[I | None, O | None, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def iter_decode(self) -> ta.Generator[O | None, I | None, None]:
        raise NotImplementedError

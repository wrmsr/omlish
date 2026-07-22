import abc

from ... import lang
from ..coro.stepped import BytesSteppedCoro
from ..coro.stepped import BytesSteppedReaderCoro


##


class Compression(lang.Abstract):
    @abc.abstractmethod
    def compress(self, d: lang.Bytes) -> lang.Bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def decompress(self, d: lang.Bytes) -> lang.Bytes:
        raise NotImplementedError


class IncrementalCompression(lang.Abstract):
    @abc.abstractmethod
    def compress_incremental(self) -> BytesSteppedCoro[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def decompress_incremental(self) -> BytesSteppedReaderCoro[None]:
        raise NotImplementedError

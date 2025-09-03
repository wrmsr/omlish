import abc

from ... import lang
from ..coro import BytesSteppedCoro
from ..coro import BytesSteppedReaderCoro


##


class Compression(lang.Abstract):
    @abc.abstractmethod
    def compress(self, d: bytes) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def decompress(self, d: bytes) -> bytes:
        raise NotImplementedError


class IncrementalCompression(lang.Abstract):
    @abc.abstractmethod
    def compress_incremental(self) -> BytesSteppedCoro[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def decompress_incremental(self) -> BytesSteppedReaderCoro[None]:
        raise NotImplementedError

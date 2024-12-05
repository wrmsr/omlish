import abc

from ...generators.readers import BytesSteppedReaderGenerator
from ...generators.stepped import BytesSteppedGenerator


class Compression(abc.ABC):
    @abc.abstractmethod
    def compress(self, d: bytes) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def decompress(self, d: bytes) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def compress_incremental(self) -> BytesSteppedGenerator[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def decompress_incremental(self) -> BytesSteppedReaderGenerator[None]:
        raise NotImplementedError

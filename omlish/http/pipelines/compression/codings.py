# ruff: noqa: UP006 UP045
# @omlish-lite
import abc
import typing as ta
import zlib

from ....io.streams.types import BytesLike
from ....lite.abstract import Abstract
from ....lite.namespaces import NamespaceClass


##


class IoPiplineHttpCompressorCoding(Abstract):
    @abc.abstractmethod
    def compress(
            self,
            data: BytesLike,
            /,
    ) -> ta.Optional[BytesLike]:
        raise NotImplementedError

    def flush(self) -> ta.Optional[BytesLike]:
        return None

    @abc.abstractmethod
    def finish(self) -> ta.Optional[BytesLike]:
        raise NotImplementedError



IoPiplineHttpCompressorCodings = ta.Mapping[str, ta.Callable[[], IoPiplineHttpCompressorCoding]]  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


#


class IoPiplineHttpDecompressorCoding(Abstract):
    @abc.abstractmethod
    def decompress(
            self,
            data: BytesLike,
            max_bytes: ta.Optional[int] = None,
            /,
    ) -> ta.Optional[BytesLike]:
        raise NotImplementedError

    @abc.abstractmethod
    def unconsumed_tail(self) -> ta.Optional[BytesLike]:
        raise NotImplementedError

    @abc.abstractmethod
    def finish(self) -> ta.Optional[BytesLike]:
        raise NotImplementedError


IoPiplineHttpDecompressorCodings = ta.Mapping[str, ta.Callable[[], IoPiplineHttpDecompressorCoding]]  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


##


class ZlibIoPiplineHttpCompressorCoding(IoPiplineHttpCompressorCoding):
    def __init__(self, wbits: int = 16 + zlib.MAX_WBITS) -> None:
        super().__init__()

        self._z = zlib.compressobj(wbits=wbits)

    def compress(
            self,
            data: BytesLike,
            /,
    ) -> ta.Optional[BytesLike]:
        return self._z.compress(data)

    def flush(self) -> ta.Optional[BytesLike]:
        return self._z.flush(zlib.Z_SYNC_FLUSH) or None

    def finish(self) -> ta.Optional[BytesLike]:
        return self._z.flush()


class ZlibIoPiplineHttpDecompressorCoding(IoPiplineHttpDecompressorCoding):
    def __init__(self, wbits: int = 16 + zlib.MAX_WBITS) -> None:
        super().__init__()

        self._z = zlib.decompressobj(wbits)

    def decompress(
            self,
            data: BytesLike,
            max_bytes: ta.Optional[int] = None,
            /,
    ) -> ta.Optional[BytesLike]:
        return self._z.decompress(data, max_bytes or 0)

    def unconsumed_tail(self) -> ta.Optional[BytesLike]:
        return self._z.unconsumed_tail

    def finish(self) -> ta.Optional[BytesLike]:
        return self._z.flush()


##


class DefaultIoPiplineHttpCompressionCodings(NamespaceClass):
    COMPRESSOR: ta.Final[IoPiplineHttpCompressorCodings] = {
        'gzip': ZlibIoPiplineHttpCompressorCoding,
    }

    DECOMPRESSOR: ta.Final[IoPiplineHttpDecompressorCodings] = {
        'gzip': ZlibIoPiplineHttpDecompressorCoding,
    }

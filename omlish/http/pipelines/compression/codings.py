# ruff: noqa: UP006 UP045
# @omlish-lite
import abc
import typing as ta
import zlib

from ....io.streams.types import BytesLike
from ....lite.abstract import Abstract
from ....lite.namespaces import NamespaceClass


##


class IoPiplineHttpCompressionCoding(Abstract):
    pass  # TODO


IoPiplineHttpCompressionCodings = ta.Mapping[str, ta.Callable[[], IoPiplineHttpCompressionCoding]]  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


#


class IoPiplineHttpDecompressionCoding(Abstract):
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
    def flush(self) -> ta.Optional[BytesLike]:
        raise NotImplementedError


IoPiplineHttpDeompressionCodings = ta.Mapping[str, ta.Callable[[], IoPiplineHttpDecompressionCoding]]  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


##


class ZlibIoPiplineHttpDecompressionCoding(IoPiplineHttpDecompressionCoding):
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

    def flush(self) -> ta.Optional[BytesLike]:
        return self._z.flush()


##


class DefaultIoPiplineHttpCompressionCodings(NamespaceClass):
    COMPRESSION: ta.Final[IoPiplineHttpCompressionCodings] = {}

    DECOMPRESSION: ta.Final[IoPiplineHttpDeompressionCodings] = {
        'zlib': ZlibIoPiplineHttpDecompressionCoding,
    }

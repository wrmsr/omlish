import dataclasses as dc
import functools
import typing as ta

from ... import lang
from ..generators import BytesSteppedGenerator
from ..generators import BytesSteppedReaderGenerator
from .adapters import CompressorObjectIncrementalAdapter
from .adapters import DecompressorObjectIncrementalAdapter
from .base import Compression
from .base import IncrementalCompression


if ta.TYPE_CHECKING:
    import bz2
else:
    bz2 = lang.proxy_import('bz2')


@dc.dataclass(frozen=True, kw_only=True)
class Bz2Compression(Compression, IncrementalCompression):
    level: int = 9

    def compress(self, d: bytes) -> bytes:
        return bz2.compress(
            d,
            self.level,
        )

    def decompress(self, d: bytes) -> bytes:
        return bz2.decompress(
            d,
        )

    def compress_incremental(self) -> BytesSteppedGenerator[None]:
        return lang.nextgen(CompressorObjectIncrementalAdapter(
            functools.partial(
                bz2.BZ2Compressor,  # type: ignore
                self.level,
            ),
        )())

    def decompress_incremental(self) -> BytesSteppedReaderGenerator[None]:
        return DecompressorObjectIncrementalAdapter(
            bz2.BZ2Decompressor,  # type: ignore
            trailing_error=OSError,
        )()

import dataclasses as dc
import functools
import typing as ta

from ... import lang
from ..coro import BytesSteppedCoro
from ..coro import BytesSteppedReaderCoro
from .adapters import CompressorObjectIncrementalAdapter
from .adapters import DecompressorObjectIncrementalAdapter
from .base import Compression
from .base import IncrementalCompression
from .codecs import make_compression_codec
from .codecs import make_compression_lazy_loaded_codec


if ta.TYPE_CHECKING:
    import bz2
else:
    bz2 = lang.proxy_import('bz2')


##


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

    def compress_incremental(self) -> BytesSteppedCoro[None]:
        return lang.nextgen(CompressorObjectIncrementalAdapter(
            functools.partial(
                bz2.BZ2Compressor,  # type: ignore
                self.level,
            ),
        )())

    def decompress_incremental(self) -> BytesSteppedReaderCoro[None]:
        return DecompressorObjectIncrementalAdapter(
            bz2.BZ2Decompressor,  # type: ignore
            trailing_error=OSError,
        )()


##


BZ2_CODEC = make_compression_codec('bz2', Bz2Compression)

# @omlish-manifest
_BZ2_LAZY_CODEC = make_compression_lazy_loaded_codec(__name__, 'BZ2_CODEC', BZ2_CODEC)

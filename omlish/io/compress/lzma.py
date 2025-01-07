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
    import lzma
else:
    lzma = lang.proxy_import('lzma')


##


@dc.dataclass(frozen=True, kw_only=True)
class LzmaCompression(Compression, IncrementalCompression):
    format: int | None = None

    check: int = -1
    preset: int | None = None
    filters: dict | None = None

    mem_limit: int | None = None

    def compress(self, d: bytes) -> bytes:
        return lzma.compress(
            d,
            format=self.format if self.format is not None else lzma.FORMAT_XZ,
            check=self.check,
            preset=self.preset,
            filters=self.filters,  # type: ignore[arg-type]
        )

    def decompress(self, d: bytes) -> bytes:
        return lzma.decompress(
            d,
            format=self.format if self.format is not None else lzma.FORMAT_AUTO,
            memlimit=self.mem_limit,
            filters=self.filters,  # type: ignore[arg-type]
        )

    def compress_incremental(self) -> BytesSteppedCoro[None]:
        return lang.nextgen(CompressorObjectIncrementalAdapter(
            functools.partial(  # type: ignore
                lzma.LZMACompressor,
                format=self.format if self.format is not None else lzma.FORMAT_XZ,
                check=self.check,
                preset=self.preset,
                filters=self.filters,  # type: ignore[arg-type]
            ),
        )())

    def decompress_incremental(self) -> BytesSteppedReaderCoro[None]:
        return DecompressorObjectIncrementalAdapter(
            functools.partial(  # type: ignore
                lzma.LZMADecompressor,
                format=self.format if self.format is not None else lzma.FORMAT_AUTO,
                memlimit=self.mem_limit,
                filters=self.filters,  # type: ignore[arg-type]
            ),
            trailing_error=lzma.LZMAError,
        )()


##


LZMA_CODEC = make_compression_codec('lzma', LzmaCompression)

# @omlish-manifest
_LZMA_LAZY_CODEC = make_compression_lazy_loaded_codec(__name__, 'LZMA_CODEC', LZMA_CODEC)

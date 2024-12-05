import dataclasses as dc
import functools
import typing as ta

from ... import lang
from ..generators import BytesSteppedGenerator
from ..generators import BytesSteppedReaderGenerator
from .adapters import CompressorObjectIncrementalAdapter
from .adapters import DecompressorObjectIncrementalAdapter
from .base import Compression


if ta.TYPE_CHECKING:
    import lzma
else:
    lzma = lang.proxy_import('lzma')


@dc.dataclass(frozen=True, kw_only=True)
class LzmaCompression(Compression):
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
            filters=self.filters,
        )

    def decompress(self, d: bytes) -> bytes:
        return lzma.decompress(
            d,
            format=self.format if self.format is not None else lzma.FORMAT_AUTO,
            memlimit=self.mem_limit,
            filters=self.filters,
        )

    def compress_incremental(self) -> BytesSteppedGenerator[None]:
        return lang.nextgen(CompressorObjectIncrementalAdapter(
            functools.partial(  # type: ignore
                lzma.LZMACompressor,
                format=self.format if self.format is not None else lzma.FORMAT_XZ,
                check=self.check,
                preset=self.preset,
                filters=self.filters,
            ),
        )())

    def decompress_incremental(self) -> BytesSteppedReaderGenerator[None]:
        return DecompressorObjectIncrementalAdapter(
            functools.partial(  # type: ignore
                lzma.LZMADecompressor,
                format=self.format if self.format is not None else lzma.FORMAT_AUTO,
                memlimit=self.mem_limit,
                filters=self.filters,
            ),
            trailing_error=lzma.LZMAError,
        )()

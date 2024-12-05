import dataclasses as dc
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
    def compress(self, d: bytes) -> bytes:
        return lzma.compress(d)

    def decompress(self, d: bytes) -> bytes:
        return lzma.decompress(d)

    def compress_incremental(self) -> BytesSteppedGenerator[None]:
        return lang.nextgen(CompressorObjectIncrementalAdapter(
            lzma.LZMACompressor,  # type: ignore
        )())

    def decompress_incremental(self) -> BytesSteppedReaderGenerator[None]:
        return DecompressorObjectIncrementalAdapter(
            lzma.LZMADecompressor,  # type: ignore
            trailing_error=lzma.LZMAError,
        )()

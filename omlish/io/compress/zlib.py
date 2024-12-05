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
    import zlib
else:
    zlib = lang.proxy_import('zlib')


@dc.dataclass(frozen=True, kw_only=True)
class ZlibCompression(Compression):
    level: int = 9

    def compress(self, d: bytes) -> bytes:
        return zlib.compress(d, self.level)

    def decompress(self, d: bytes) -> bytes:
        return zlib.decompress(d)

    def compress_incremental(self) -> BytesSteppedGenerator[None]:
        return lang.nextgen(CompressorObjectIncrementalAdapter(
            functools.partial(
                zlib.compressobj,  # type: ignore
                self.level,
            ),
        )())

    def decompress_incremental(self) -> BytesSteppedReaderGenerator[None]:
        return DecompressorObjectIncrementalAdapter(
            zlib.decompressobj,  # type: ignore
            trailing_error=OSError,
        )()

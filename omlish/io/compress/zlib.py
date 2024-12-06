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
    import zlib
else:
    zlib = lang.proxy_import('zlib')


@dc.dataclass(frozen=True, kw_only=True)
class ZlibCompression(Compression, IncrementalCompression):
    level: int = 9

    wbits: int | None = None
    strategy: int | None = None
    zdict: bytes | None = None

    def compress(self, d: bytes) -> bytes:
        return zlib.compress(
            d,
            self.level,
            **(dict(wbits=self.wbits) if self.wbits is not None else {}),
        )

    def decompress(self, d: bytes) -> bytes:
        return zlib.decompress(
            d,
            **(dict(wbits=self.wbits) if self.wbits is not None else {}),
        )

    def compress_incremental(self) -> BytesSteppedGenerator[None]:
        return lang.nextgen(CompressorObjectIncrementalAdapter(
            functools.partial(
                zlib.compressobj,  # type: ignore
                self.level,
                **(dict(wbits=self.wbits) if self.wbits is not None else {}),  # type: ignore[arg-type]
                **(dict(strategy=self.strategy) if self.strategy is not None else {}),  # type: ignore[arg-type]
                **(dict(zdict=self.zdict) if self.zdict is not None else {}),  # type: ignore[arg-type]
            ),
        )())

    def decompress_incremental(self) -> BytesSteppedReaderGenerator[None]:
        return DecompressorObjectIncrementalAdapter(
            functools.partial(  # type: ignore
                zlib.decompressobj,
                **(dict(wbits=self.wbits) if self.wbits is not None else {}),  # type: ignore[arg-type]
                **(dict(zdict=self.zdict) if self.zdict is not None else {}),  # type: ignore[arg-type]
            ),
            trailing_error=OSError,
        )()

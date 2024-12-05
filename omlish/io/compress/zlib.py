import functools
import typing as ta

from ... import lang
from ..generators import BytesSteppedGenerator
from ..generators import BytesSteppedReaderGenerator
from .adapters import CompressorObjectIncrementalAdapter
from .adapters import DecompressorObjectIncrementalAdapter


if ta.TYPE_CHECKING:
    import zlib
else:
    zlib = lang.proxy_import('zlib')


class IncrementalZlibCompressor:
    def __init__(
            self,
            *,
            compresslevel: int = 9,
    ) -> None:
        super().__init__()

        self._compresslevel = compresslevel

    @lang.autostart
    def __call__(self) -> BytesSteppedGenerator:
        return CompressorObjectIncrementalAdapter(
            functools.partial(
                zlib.compressobj,  # type: ignore
                self._compresslevel,
            ),
        )()


class IncrementalZlibDecompressor:
    def __call__(self) -> BytesSteppedReaderGenerator:
        return DecompressorObjectIncrementalAdapter(
            zlib.decompressobj,  # type: ignore
            trailing_error=OSError,
        )()

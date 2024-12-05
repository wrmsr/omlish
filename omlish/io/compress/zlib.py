import functools
import typing as ta

from ... import lang
from .adapters import CompressorIncrementalAdapter
from .adapters import DecompressorIncrementalAdapter
from .types import IncrementalCompressor
from .types import IncrementalDecompressor


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
    def __call__(self) -> IncrementalCompressor:
        return CompressorIncrementalAdapter(
            functools.partial(
                zlib.compressobj,  # type: ignore
                self._compresslevel,
            ),
        )()


class IncrementalZlibDecompressor:
    def __call__(self) -> IncrementalDecompressor:
        return DecompressorIncrementalAdapter(
            zlib.decompressobj,  # type: ignore
            trailing_error=OSError,
        )()

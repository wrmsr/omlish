import functools
import typing as ta

from ... import lang
from .adapters import CompressorIncrementalAdapter
from .adapters import DecompressorIncrementalAdapter
from .types import IncrementalCompressor
from .types import IncrementalDecompressor


if ta.TYPE_CHECKING:
    import bz2
else:
    bz2 = lang.proxy_import('bz2')


class IncrementalBz2Compressor:
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
                bz2.BZ2Compressor,  # type: ignore
                self._compresslevel,
            ),
        )()


class IncrementalBz2Decompressor:
    def __call__(self) -> IncrementalDecompressor:
        return DecompressorIncrementalAdapter(
            bz2.BZ2Decompressor,  # type: ignore
            trailing_error=OSError,
        )()

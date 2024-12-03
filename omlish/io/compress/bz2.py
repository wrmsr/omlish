import bz2
import functools

from .adapters import CompressorIncrementalAdapter
from .adapters import DecompressorIncrementalAdapter
from .types import IncrementalCompressor
from .types import IncrementalDecompressor


class IncrementalBz2Compressor:
    def __init__(
            self,
            *,
            compresslevel: int = 9,
    ) -> None:
        super().__init__()

        self._compresslevel = compresslevel

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

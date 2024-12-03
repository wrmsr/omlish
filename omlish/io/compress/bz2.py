import bz2

from .adapters import CompressorIncrementalAdapter
from .adapters import DecompressorIncrementalAdapter
from .types import IncrementalCompressor
from .types import IncrementalDecompressor


class IncrementalBz2Compressor:
    def __call__(self) -> IncrementalCompressor:
        return CompressorIncrementalAdapter(
            bz2.BZ2Compressor,  # type: ignore
        )()


class IncrementalBz2Decompressor:
    def __call__(self) -> IncrementalDecompressor:
        return DecompressorIncrementalAdapter(
            bz2.BZ2Decompressor,  # type: ignore
            trailing_error=OSError,
        )()

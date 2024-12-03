import bz2

from .adapters import DecompressorIncrementalAdapter
from .types import IncrementalDecompressor


class IncrementalBz2Decompressor:
    def __call__(self) -> IncrementalDecompressor:
        return DecompressorIncrementalAdapter(
            bz2.BZ2Decompressor,  # type: ignore
            trailing_error=OSError,
        )()

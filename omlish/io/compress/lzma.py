import typing as ta

from ... import lang
from .adapters import CompressorIncrementalAdapter
from .adapters import DecompressorIncrementalAdapter
from .types import IncrementalCompressor
from .types import IncrementalDecompressor


if ta.TYPE_CHECKING:
    import lzma
else:
    lzma = lang.proxy_import('lzma')


class IncrementalLzmaCompressor:
    def __init__(self) -> None:
        super().__init__()

    def __call__(self) -> IncrementalCompressor:
        return CompressorIncrementalAdapter(
            lzma.LZMACompressor,  # type: ignore
        )()


class IncrementalLzmaDecompressor:
    def __call__(self) -> IncrementalDecompressor:
        return DecompressorIncrementalAdapter(
            lzma.LZMADecompressor,  # type: ignore
            trailing_error=lzma.LZMAError,
        )()

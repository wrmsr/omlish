import typing as ta

from ... import lang
from ..generators import BytesSteppedGenerator
from ..generators import BytesSteppedReaderGenerator
from .adapters import CompressorObjectIncrementalAdapter
from .adapters import DecompressorObjectIncrementalAdapter


if ta.TYPE_CHECKING:
    import lzma
else:
    lzma = lang.proxy_import('lzma')


class IncrementalLzmaCompressor:
    def __init__(self) -> None:
        super().__init__()

    @lang.autostart
    def __call__(self) -> BytesSteppedGenerator:
        return CompressorObjectIncrementalAdapter(
            lzma.LZMACompressor,  # type: ignore
        )()


class IncrementalLzmaDecompressor:
    def __call__(self) -> BytesSteppedReaderGenerator:
        return DecompressorObjectIncrementalAdapter(
            lzma.LZMADecompressor,  # type: ignore
            trailing_error=lzma.LZMAError,
        )()

import functools
import typing as ta

from ... import lang
from ..generators import BytesSteppedGenerator
from ..generators import BytesSteppedReaderGenerator
from .adapters import CompressorObjectIncrementalAdapter
from .adapters import DecompressorObjectIncrementalAdapter


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
    def __call__(self) -> BytesSteppedGenerator:
        return CompressorObjectIncrementalAdapter(
            functools.partial(
                bz2.BZ2Compressor,  # type: ignore
                self._compresslevel,
            ),
        )()


class IncrementalBz2Decompressor:
    def __call__(self) -> BytesSteppedReaderGenerator:
        return DecompressorObjectIncrementalAdapter(
            bz2.BZ2Decompressor,  # type: ignore
            trailing_error=OSError,
        )()

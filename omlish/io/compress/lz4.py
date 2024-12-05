import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ..generators import BytesSteppedGenerator
from ..generators import BytesSteppedReaderGenerator
from .base import Compression


if ta.TYPE_CHECKING:
    import lz4.frame as lz4_frame
else:
    lz4_frame = lang.proxy_import('lz4.frame')


@dc.dataclass(frozen=True, kw_only=True)
class Lz4Compression(Compression):
    level: int = 0

    def compress(self, d: bytes) -> bytes:
        return lz4_frame.compress(d, compression_level=self.level)

    def decompress(self, d: bytes) -> bytes:
        return lz4_frame.decompress(d)

    @lang.autostart
    def compress_incremental(self) -> BytesSteppedGenerator[None]:
        with lz4_frame.LZ4FrameCompressor() as compressor:
            started = False
            while True:
                i = check.isinstance((yield None), bytes)
                if not started:
                    yield compressor.begin()
                    started = True
                if not i:
                    yield compressor.flush()
                    yield b''
                    return
                if (o := compressor.compress(i)):
                    yield o

    def decompress_incremental(self) -> BytesSteppedReaderGenerator[None]:
        # with lz4_frame.LZ4FrameDecompressor() as decompressor:
        #     decompressed = decompressor.decompress(compressed[:len(compressed) // 2])
        #     decompressed += decompressor.decompress(compressed[len(compressed) // 2:])
        raise NotImplementedError

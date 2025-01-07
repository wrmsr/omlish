import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ..coro import BytesSteppedCoro
from .base import Compression
from .base import IncrementalCompression
from .codecs import make_compression_codec
from .codecs import make_compression_lazy_loaded_codec


if ta.TYPE_CHECKING:
    import lz4.frame as lz4_frame
else:
    lz4_frame = lang.proxy_import('lz4.frame')


##


@dc.dataclass(frozen=True, kw_only=True)
class Lz4Compression(Compression, IncrementalCompression):
    level: int = 0

    block_size: int = 0
    block_linked: bool = True
    block_checksum: bool = False
    content_checksum: bool = False
    store_size: bool = True
    auto_flush: bool = False

    def compress(self, d: bytes) -> bytes:
        return lz4_frame.compress(
            d,
            compression_level=self.level,
            block_size=self.block_size,
            content_checksum=self.content_checksum,
            block_linked=self.block_linked,
            store_size=self.store_size,
        )

    def decompress(self, d: bytes) -> bytes:
        return lz4_frame.decompress(
            d,
        )

    @lang.autostart
    def compress_incremental(self) -> BytesSteppedCoro[None]:
        with lz4_frame.LZ4FrameCompressor(
                compression_level=self.level,
                block_size=self.block_size,
                block_linked=self.block_linked,
                block_checksum=self.block_checksum,
                content_checksum=self.content_checksum,
                auto_flush=self.auto_flush,
        ) as compressor:
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

    @lang.autostart
    def decompress_incremental(self) -> BytesSteppedCoro[None]:
        # lz4 lib does internal buffering so this is simply a BytesSteppedCoro not a BytesSteppedReaderCoro as it
        # only yields None, accepting any number of bytes at a time.
        with lz4_frame.LZ4FrameDecompressor() as decompressor:
            while True:
                i = check.isinstance((yield None), bytes)
                if not i:
                    yield b''
                    return
                if (o := decompressor.decompress(i)):
                    yield o


##


LZ4_CODEC = make_compression_codec('lz4', Lz4Compression)

# @omlish-manifest
_LZ4_LAZY_CODEC = make_compression_lazy_loaded_codec(__name__, 'LZ4_CODEC', LZ4_CODEC)

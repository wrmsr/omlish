import dataclasses as dc
import typing as ta

from ... import lang
from .base import Compression
from .codecs import make_compression_codec
from .codecs import make_compression_lazy_loaded_codec


if ta.TYPE_CHECKING:
    import brotli
else:
    brotli = lang.proxy_import('brotli')


##


@dc.dataclass(frozen=True, kw_only=True)
class BrotliCompression(Compression):
    mode: int | None = None
    quality: int | None = None
    lgwin: int | None = None
    lgblock: int | None = None

    def compress(self, d: bytes) -> bytes:
        return brotli.compress(
            d,
            **(dict(mode=self.mode) if self.mode is not None else {}),
            **(dict(quality=self.quality) if self.quality is not None else {}),
            **(dict(lgwin=self.lgwin) if self.lgwin is not None else {}),
            **(dict(lgblock=self.lgblock) if self.lgblock is not None else {}),
        )

    def decompress(self, d: bytes) -> bytes:
        return brotli.decompress(
            d,
        )


##


BROTLI_CODEC = make_compression_codec('brotli', BrotliCompression)

# @omlish-manifest
_BROTLI_LAZY_CODEC = make_compression_lazy_loaded_codec(__name__, 'BROTLI_CODEC', BROTLI_CODEC)

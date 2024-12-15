import dataclasses as dc
import typing as ta

from ... import lang
from .base import Compression
from .codecs import make_compression_codec
from .codecs import make_compression_lazy_loaded_codec


if ta.TYPE_CHECKING:
    import zstandard
else:
    zstandard = lang.proxy_import('zstandard')


##


@dc.dataclass(frozen=True, kw_only=True)
class ZstdCompression(Compression):
    level: int | None = None

    max_output_size: int = 0

    def compress(self, d: bytes) -> bytes:
        return zstandard.compress(
            d,
            **(dict(level=self.level) if self.level is not None else {}),
        )

    def decompress(self, d: bytes) -> bytes:
        return zstandard.decompress(
            d,
            max_output_size=self.max_output_size,
        )


##


ZSTD_CODEC = make_compression_codec('zstd', ZstdCompression)

# @omlish-manifest
_ZSTD_LAZY_CODEC = make_compression_lazy_loaded_codec(__name__, 'ZSTD_CODEC', ZSTD_CODEC)

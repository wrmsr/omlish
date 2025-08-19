import dataclasses as dc
import sys
import typing as ta

from ... import lang
from .base import Compression
from .codecs import make_compression_codec
from .codecs import make_compression_lazy_loaded_codec


if sys.version_info >= (3, 14):
    if ta.TYPE_CHECKING:
        from compression import zstd  # noqa
    else:
        zstd = lang.proxy_import('compression.zstd')

else:  # noqa
    if ta.TYPE_CHECKING:
        import zstandard as zstd
    else:
        zstd = lang.proxy_import('zstandard')


##


@dc.dataclass(frozen=True, kw_only=True)
class ZstdCompression(Compression):
    level: int | None = None

    # max_output_size: int = 0

    def compress(self, d: bytes) -> bytes:
        return zstd.compress(
            d,
            **(dict(level=self.level) if self.level is not None else {}),
        )

    def decompress(self, d: bytes) -> bytes:
        return zstd.decompress(
            d,
            # max_output_size=self.max_output_size,
        )


##


ZSTD_CODEC = make_compression_codec('zstd', ZstdCompression)

# @omlish-manifest
_ZSTD_LAZY_CODEC = make_compression_lazy_loaded_codec(__name__, 'ZSTD_CODEC', ZSTD_CODEC)

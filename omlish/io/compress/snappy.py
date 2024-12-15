import dataclasses as dc
import typing as ta

from ... import lang
from .base import Compression
from .codecs import make_compression_codec
from .codecs import make_compression_lazy_loaded_codec


if ta.TYPE_CHECKING:
    import snappy
else:
    snappy = lang.proxy_import('snappy')


##


@dc.dataclass(frozen=True)
class SnappyCompression(Compression):
    def compress(self, d: bytes) -> bytes:
        return snappy.compress(d)

    def decompress(self, d: bytes) -> bytes:
        return snappy.decompress(d)


##


SNAPPY_CODEC = make_compression_codec('snappy', SnappyCompression)

# @omlish-manifest
_SNAPPY_LAZY_CODEC = make_compression_lazy_loaded_codec(__name__, 'SNAPPY_CODEC', SNAPPY_CODEC)

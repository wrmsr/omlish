import dataclasses as dc
import typing as ta

from ... import lang
from .base import Compression


if ta.TYPE_CHECKING:
    import snappy
else:
    snappy = lang.proxy_import('snappy')


@dc.dataclass(frozen=True)
class SnappyCompression(Compression):
    def compress(self, d: bytes) -> bytes:
        return snappy.compress(d)

    def decompress(self, d: bytes) -> bytes:
        return snappy.decompress(d)

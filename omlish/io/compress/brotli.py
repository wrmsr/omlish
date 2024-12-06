import dataclasses as dc
import typing as ta

from ... import lang
from .base import Compression


if ta.TYPE_CHECKING:
    import brotli
else:
    brotli = lang.proxy_import('brotli')


@dc.dataclass(frozen=True, kw_only=True)
class SnappyCompression(Compression):
    mode: int | None = None
    quality: int | None = None
    lgwin: int | None = None
    lgblock: int | None = None

    def compress(self, d: bytes) -> bytes:
        return brotli.compress(
            d,
            **(dict(mode=self.mode) if self.mode is not None else {}),
            **(dict(mode=self.quality) if self.quality is not None else {}),
            **(dict(mode=self.lgwin) if self.lgwin is not None else {}),
            **(dict(mode=self.lgblock) if self.lgblock is not None else {}),
        )

    def decompress(self, d: bytes) -> bytes:
        return brotli.decompress(
            d,
        )

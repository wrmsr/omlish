import dataclasses as dc
import typing as ta

from ... import lang
from .base import Compression


if ta.TYPE_CHECKING:
    import zstandard
else:
    zstandard = lang.proxy_import('zstandard')


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

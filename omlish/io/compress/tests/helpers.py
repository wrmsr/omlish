import typing as ta

from .... import lang
from ...generators.stepped import joined_bytes_stepped_generator
from ..types import IncrementalCompressor


def feed_inc_compressor(
        g: IncrementalCompressor,
        f: ta.IO,
        *,
        read_size: int = 4096,
) -> ta.Iterator[bytes]:
    yield from lang.genmap(
        joined_bytes_stepped_generator(g),
        lang.readiter(f, read_size),
    )

import functools
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
    fi = iter(functools.partial(f.read, read_size), None)
    fg = joined_bytes_stepped_generator(g)
    mi = lang.GeneratorMappedIterator(fg, fi)
    yield from mi

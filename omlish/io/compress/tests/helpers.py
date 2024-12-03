import typing as ta

from ..types import IncrementalCompressor


def feed_inc_compressor(
        g: IncrementalCompressor,
        f: ta.IO,
        *,
        read_size: int = 4096,
) -> ta.Iterator[bytes]:
    i = None
    while True:
        o = g.send(i)
        i = None

        if o is None:
            i = f.read(read_size)
            if len(i) != read_size:
                break
        elif not o:
            raise TypeError(o)
        else:
            yield o

    o = g.send(i)
    while True:
        if o is None:
            break
        elif not o:
            raise TypeError(o)
        else:
            yield o

        try:
            o = g.send(None)
        except StopIteration:
            if i:
                raise RuntimeError  # noqa

    if i:
        try:
            o = g.send(b'')
        except StopIteration:
            pass

        else:
            while True:
                if o is None:
                    raise TypeError(o)
                elif not o:
                    break
                else:
                    yield o

                try:
                    o = g.send(None)
                except StopIteration:
                    break

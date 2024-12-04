import typing as ta

from ..types import IncrementalCompressor


def _yield_read_chunks(
        f: ta.IO,
        read_size: int = 4096,
) -> ta.Iterator[bytes]:
    while True:
        d = f.read(read_size)
        yield d
        if len(d) != read_size:
            break
    if d:
        yield b''


def feed_inc_compressor(
        g: IncrementalCompressor,
        f: ta.IO,
        *,
        read_size: int = 4096,
) -> ta.Iterator[bytes]:
    chunks = _yield_read_chunks(f, read_size)

    i = None
    while True:
        o = g.send(i)
        i = None

        if o is None:
            if not (i := next(chunks, None)):
                break
        elif not o:
            raise EOFError
        else:
            yield o

    while True:
        o = g.send(i)
        i = None

        if o is None:
            raise EOFError
        elif not o:
            break
        else:
            yield o

    if o != b'':
        raise EOFError

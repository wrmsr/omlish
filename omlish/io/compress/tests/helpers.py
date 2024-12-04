import typing as ta

from .... import lang
from ..types import IncrementalCompressor


I = ta.TypeVar('I')
O = ta.TypeVar('O')
R = ta.TypeVar('R')


##


def buffer_generator_writer(
        g: ta.Generator[O | None, I | None, R],
        *,
        terminator: lang.Maybe[O] = lang.empty(),
) -> ta.Generator[list[O], I, R]:
    l: list[O]
    i: I | None = yield  # type: ignore
    while True:
        l = []
        while True:
            try:
                o = g.send(i)
            except StopIteration as e:
                if l:
                    yield l
                return e.value
            i = None
            if o is None:
                break
            l.append(o)
            if terminator.present and o == terminator.must():
                if l:
                    yield l
                raise StopIteration
        i = yield l


##


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

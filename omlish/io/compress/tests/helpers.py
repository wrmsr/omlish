import typing as ta

from .... import lang
from ..types import IncrementalCompressor


T = ta.TypeVar('T')
I = ta.TypeVar('I')
O = ta.TypeVar('O')
OF = ta.TypeVar('OF')
OT = ta.TypeVar('OT')
R = ta.TypeVar('R')


##


def flatmap_generator_writer(
        fn: ta.Callable[[list[OF]], OT],
        g: ta.Generator[OF | None, I | None, R],
        *,
        terminator: lang.Maybe[OF] = lang.empty(),
) -> ta.Generator[OT, I, R]:
    l: list[OF]
    i: I | None = yield  # type: ignore
    while True:
        l = []
        while True:
            try:
                o = g.send(i)
            except StopIteration as e:
                if l:
                    yield fn(l)
                return e.value
            i = None
            if o is None:
                break
            l.append(o)
            if terminator.present and o == terminator.must():
                if l:
                    yield fn(l)
                raise StopIteration
        i = yield fn(l)


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

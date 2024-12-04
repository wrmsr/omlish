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


@lang.autostart
def flatmap_stepped_generator(
        fn: ta.Callable[[list[OF]], OT],
        g: ta.Generator[OF | None, I | None, R],
        *,
        terminate: ta.Callable[[OF], bool] | None = None,
) -> ta.Generator[OT, I, lang.Maybe[R]]:
    """
    Given a 'stepped generator' - a generator which accepts input items and yields zero or more non-None values in
    response until it signals it's ready for the next input by yielding None - and a function taking a list, returns a
    1:1 generator which accepts input, builds a list of yielded generator output, calls the given function with that
    list, and yields the result.

    An optional terminate function may be provided which will cause this function to return early if it returns true for
    an encountered yielded value. The encountered value causing termination will be included in the list sent to the
    given fn.

    Returns a Maybe of either the given generator's return value or empty if the terminator was encountered.
    """

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
                return lang.just(e.value)

            i = None

            if o is None:
                break

            l.append(o)

            if terminate is not None and terminate(o):
                yield fn(l)
                return lang.empty()

        i = yield fn(l)


##


def join_bytes(l: ta.Sequence[bytes]) -> bytes:
    if not l:
        return b''
    elif len(l) == 1:
        return l[0]
    else:
        return b''.join(l)


def join_str(l: ta.Sequence[str]) -> str:
    if not l:
        return ''
    elif len(l) == 1:
        return l[0]
    else:
        return ''.join(l)


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

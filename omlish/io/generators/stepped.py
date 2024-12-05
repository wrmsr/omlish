import typing as ta

from ... import lang
from .consts import DEFAULT_BUFFER_SIZE


T = ta.TypeVar('T')
I = ta.TypeVar('I')
O = ta.TypeVar('O')
OF = ta.TypeVar('OF')
OT = ta.TypeVar('OT')
R = ta.TypeVar('R')


SteppedGenerator: ta.TypeAlias = ta.Generator[O | None, I | None, R]

BytesSteppedGenerator: ta.TypeAlias = SteppedGenerator[bytes, bytes, R]
StrSteppedGenerator: ta.TypeAlias = SteppedGenerator[str, str, R]


##


@lang.autostart
def flatmap_stepped_generator(
        fn: ta.Callable[[list[OF]], OT],
        g: SteppedGenerator[OF, I, R],
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


def _join_bytes(l: ta.Sequence[bytes]) -> bytes:
    if not l:
        return b''
    elif len(l) == 1:
        return l[0]
    else:
        return b''.join(l)


def _join_str(l: ta.Sequence[str]) -> str:
    if not l:
        return ''
    elif len(l) == 1:
        return l[0]
    else:
        return ''.join(l)


def _is_empty(o: T) -> bool:
    return len(o) < 1  # type: ignore


def joined_bytes_stepped_generator(
        g: ta.Generator[bytes | None, bytes | None, R],
) -> ta.Generator[bytes, bytes, R]:
    return flatmap_stepped_generator(_join_bytes, g, terminate=_is_empty)


def joined_str_stepped_generator(
        g: ta.Generator[str | None, str | None, R],
) -> ta.Generator[str, str, R]:
    return flatmap_stepped_generator(_join_str, g, terminate=_is_empty)


##


def read_into_bytes_stepped_generator(
        g: BytesSteppedGenerator,
        f: ta.IO,
        *,
        read_size: int = DEFAULT_BUFFER_SIZE,
) -> ta.Iterator[bytes]:
    yield from lang.genmap(  # type: ignore[misc]
        joined_bytes_stepped_generator(g),
        lang.readiter(f, read_size),
    )
